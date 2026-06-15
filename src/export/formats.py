"""Format conversion and download — all supported output formats in one place.

HAR-confirmed facts (2026-06-15):
  - /api/file-proxy returns Content-Type: image/jpeg regardless of the S3 path suffix.
    PNG and JPG are the same bytes; the extension is chosen client-side.
  - /app-api/plot/image/svg converts the image server-side and returns an S3 SVG URL.
  - PPTX has no server-side endpoint. The web UI generates it client-side from the SVG
    (browser JS, likely pptxgenjs). We replicate this locally with python-pptx.
"""

import os
from typing import Optional

import requests

BASE_URL = "https://chat.figurelabs.ai"
_PROXY       = f"{BASE_URL}/api/file-proxy"
_SVG_CONVERT = f"{BASE_URL}/app-api/plot/image/svg"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _stem_from_url(url: str) -> str:
    part = url.split("/")[-1].split("?")[0]
    return part.rsplit(".", 1)[0] or "figure"


def _write_stream(resp: requests.Response, path: str) -> str:
    with open(path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
    return path


def _fetch_via_proxy(
    session: requests.Session,
    s3_url: str,
    ext: str,
    output_dir: str,
    filename: Optional[str],
) -> Optional[str]:
    """Download any S3 resource through the file-proxy and save with the given extension."""
    resp = session.get(_PROXY, params={"url": s3_url}, stream=True)
    if resp.status_code != 200:
        print(f"[{ext}] proxy HTTP {resp.status_code}")
        return None
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{filename or _stem_from_url(s3_url)}.{ext}")
    _write_stream(resp, path)
    print(f"[{ext}] {path} ({os.path.getsize(path) // 1024} KB)")
    return path


def _request_svg_url(session: requests.Session, png_s3_url: str) -> Optional[str]:
    """POST to the SVG conversion endpoint and return the resulting S3 URL."""
    resp = session.post(_SVG_CONVERT, json={"imageUrl": [png_s3_url]})
    if resp.status_code != 200:
        print(f"[svg] conversion HTTP {resp.status_code}")
        return None
    result = resp.json()
    if result.get("code") != 0:
        print(f"[svg] conversion failed: {result.get('msg', result)}")
        return None
    urls = result["data"].get("fileUrls", [])
    if not urls:
        print("[svg] no fileUrls in response")
        return None
    return urls[0]


# ---------------------------------------------------------------------------
# Public download functions
# ---------------------------------------------------------------------------

def download_png(
    session: requests.Session,
    png_s3_url: str,
    output_dir: str = ".",
    filename: Optional[str] = None,
) -> Optional[str]:
    # Server returns image/jpeg regardless of S3 path suffix — saved as .png for compatibility.
    return _fetch_via_proxy(session, png_s3_url, "png", output_dir, filename)


def download_jpg(
    session: requests.Session,
    png_s3_url: str,
    output_dir: str = ".",
    filename: Optional[str] = None,
) -> Optional[str]:
    # Identical bytes to PNG download; only the saved extension differs.
    return _fetch_via_proxy(session, png_s3_url, "jpg", output_dir, filename)


def download_svg(
    session: requests.Session,
    png_s3_url: str,
    output_dir: str = ".",
    filename: Optional[str] = None,
) -> Optional[str]:
    svg_url = _request_svg_url(session, png_s3_url)
    if not svg_url:
        return None
    return _fetch_via_proxy(session, svg_url, "svg", output_dir, filename)


def download_pptx(
    session: requests.Session,
    png_s3_url: str,
    output_dir: str = ".",
    filename: Optional[str] = None,
) -> Optional[str]:
    """Build a PPTX locally, replicating the web UI's client-side pptxgenjs flow.

    The web UI has no server-side PPTX endpoint (all /image/pptx variants return 404).
    Instead it lazy-loads pptxgenjs and calls addImage with the SVG file directly
    (type: image/svg+xml), producing a vector-quality PPTX.

    We replicate this exactly: fetch the server-converted SVG, embed it as a native
    SVG media part inside the PPTX ZIP using python-pptx + low-level lxml surgery.
    """
    try:
        from pptx import Presentation
        from pptx.util import Emu
        from pptx.oxml.ns import qn
        from lxml import etree
        import io, zipfile, copy
    except ImportError:
        print("[pptx] python-pptx or lxml not installed — run: uv pip install python-pptx lxml")
        return None

    # 1. Get SVG bytes from server
    svg_url = _request_svg_url(session, png_s3_url)
    if not svg_url:
        return None
    svg_resp = session.get(_PROXY, params={"url": svg_url}, stream=True)
    if svg_resp.status_code != 200:
        print(f"[pptx] SVG fetch HTTP {svg_resp.status_code}")
        return None
    svg_bytes = svg_resp.content

    # 2. Parse SVG viewBox to get aspect ratio
    try:
        root = etree.fromstring(svg_bytes)
        vb = root.get("viewBox", "")
        parts = vb.split()
        if len(parts) == 4:
            svg_w, svg_h = float(parts[2]), float(parts[3])
        else:
            w_attr = root.get("width", "1376")
            h_attr = root.get("height", "768")
            svg_w = float(''.join(c for c in w_attr if c.isdigit() or c == '.') or 1376)
            svg_h = float(''.join(c for c in h_attr if c.isdigit() or c == '.') or 768)
    except Exception:
        svg_w, svg_h = 1376.0, 768.0

    # 3. Build blank PPTX in memory
    prs = Presentation()
    # Match SVG aspect ratio; use widescreen 16:9 as baseline
    slide_w = Emu(9144000)   # 10 inches in EMU (914400 EMU/inch)
    slide_h = Emu(int(slide_w * svg_h / svg_w))
    prs.slide_width  = slide_w
    prs.slide_height = slide_h

    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank

    # 4. Save to in-memory ZIP so we can inject the SVG part manually
    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)

    # 5. Open the PPTX ZIP and inject SVG as a media part
    out_buf = io.BytesIO()
    slide_num = 1  # we added exactly one slide
    svg_part_name = f"ppt/media/image1.svg"
    slide_xml_name = f"ppt/slides/slide{slide_num}.xml"
    rels_name = f"ppt/slides/_rels/slide{slide_num}.xml.rels"
    ct_name = "[Content_Types].xml"
    # Files we will rewrite — skip them in the copy loop
    rewritten = {slide_xml_name, rels_name, ct_name}

    with zipfile.ZipFile(buf, "r") as zin, zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as zout:
        # Copy all parts except the ones we will patch
        for item in zin.infolist():
            if item.filename not in rewritten:
                zout.writestr(item, zin.read(item.filename))

        # Add SVG media part
        zout.writestr(svg_part_name, svg_bytes)
        slide_xml = zin.read(slide_xml_name)
        tree = etree.fromstring(slide_xml)

        spTree = tree.find(".//" + qn("p:spTree"))

        # Build <p:pic> element with SVG image reference (rId will be wired below)
        pic_xml = f"""<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                            xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:nvPicPr>
    <p:cNvPr id="2" name="Figure"/>
    <p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>
    <p:nvPr/>
  </p:nvPicPr>
  <p:blipFill>
    <a:blip r:embed="rId1SVG"/>
    <a:stretch><a:fillRect/></a:stretch>
  </p:blipFill>
  <p:spPr>
    <a:xfrm>
      <a:off x="0" y="0"/>
      <a:ext cx="{int(slide_w)}" cy="{int(slide_h)}"/>
    </a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
  </p:spPr>
</p:pic>"""
        pic_elem = etree.fromstring(pic_xml)
        spTree.append(pic_elem)

        # Write patched slide XML back
        zout.writestr(slide_xml_name, etree.tostring(tree, xml_declaration=True,
                                                      encoding="UTF-8", standalone=True))

        # Patch slide1.xml.rels to add SVG relationship
        try:
            rels_xml = zin.read(rels_name)
            rels_tree = etree.fromstring(rels_xml)
        except KeyError:
            rels_tree = etree.fromstring(
                b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
            )

        ns = "http://schemas.openxmlformats.org/package/2006/relationships"
        svg_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
        rel = etree.SubElement(rels_tree, f"{{{ns}}}Relationship")
        rel.set("Id", "rId1SVG")
        rel.set("Type", svg_type)
        rel.set("Target", "../media/image1.svg")
        zout.writestr(rels_name, etree.tostring(rels_tree, xml_declaration=True,
                                                 encoding="UTF-8", standalone=True))

        # Patch [Content_Types].xml to register .svg extension
        ct_xml = zin.read(ct_name)
        ct_tree = etree.fromstring(ct_xml)
        ct_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
        existing_exts = {e.get("Extension") for e in ct_tree.findall(f"{{{ct_ns}}}Default")}
        if "svg" not in existing_exts:
            svg_ct = etree.SubElement(ct_tree, f"{{{ct_ns}}}Default")
            svg_ct.set("Extension", "svg")
            svg_ct.set("ContentType", "image/svg+xml")
        zout.writestr(ct_name, etree.tostring(ct_tree, xml_declaration=True,
                                                             encoding="UTF-8", standalone=True))

    os.makedirs(output_dir, exist_ok=True)
    stem = filename or _stem_from_url(png_s3_url)
    path = os.path.join(output_dir, f"{stem}.pptx")
    with open(path, "wb") as f:
        f.write(out_buf.getvalue())

    print(f"[pptx] {path} ({os.path.getsize(path) // 1024} KB)")
    return path


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_HANDLERS = {
    "png":  download_png,
    "jpg":  download_jpg,
    "jpeg": download_jpg,
    "svg":  download_svg,
    "pptx": download_pptx,
}


def download(
    session: requests.Session,
    png_s3_url: str,
    fmt: str,
    output_dir: str = ".",
    filename: Optional[str] = None,
) -> Optional[str]:
    """Unified entry point — dispatch to the correct format handler."""
    key = fmt.lower().lstrip(".")
    handler = _HANDLERS.get(key)
    if handler is None:
        print(f"[formats] unknown format '{fmt}' — supported: {', '.join(_HANDLERS)}")
        return None
    return handler(session, png_s3_url, output_dir, filename)
