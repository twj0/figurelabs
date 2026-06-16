"""FastAPI application — REST API + static frontend hosting."""

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..config import PORT
from ..db import init_db, save_account, list_accounts, get_account, delete_account, update_label
from ..chat.client import FigureLabsChat
from ..export.client import ExportClient
from ..export.formats import _request_svg_url, _PROXY
from ..export._session import make_session
from ..register.client import FigureLabsRegistration
from ..register.mail_service import MailTmService, DuckMailService
from ..core.database import stats_db


app = FastAPI(title="FigureLabs AI", docs_url=None, redoc_url=None)


@app.on_event("startup")
async def startup():
    await init_db()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class AccountOut(BaseModel):
    id: int
    user_id: str
    email: str
    access_token: str
    mail_service: str
    created_at: int
    label: Optional[str] = None
    expires_time: Optional[int] = None


class RegisterRequest(BaseModel):
    mail_service: str = "mailtm"   # "mailtm" | "duckmail"


class RegisterResponse(BaseModel):
    # For mailtm: account is complete
    # For duckmail: needs manual code entry — returns pending_id
    done: bool
    account: Optional[AccountOut] = None
    # duckmail flow
    pending_id: Optional[str] = None
    email: Optional[str] = None
    inbox_url: Optional[str] = None


class DuckMailVerifyRequest(BaseModel):
    pending_id: str
    code: str


class LabelUpdate(BaseModel):
    label: str


class SessionCreate(BaseModel):
    access_token: str
    title: str = "New Diagram"


class SessionResponse(BaseModel):
    session_id: str


class MessageSend(BaseModel):
    access_token: str
    session_id: str
    text: str
    model_id: int = 7
    ratio: str = "16:9"


class MessageResponse(BaseModel):
    message_id: str


class StatusResponse(BaseModel):
    status: int
    image_model: Optional[str] = None
    image_ratio: Optional[str] = None
    file_url: list[str] = []


class ExpandRequest(BaseModel):
    access_token: str
    message: str


class ExpandResponse(BaseModel):
    expanded: str


# In-memory store for pending DuckMail flows {pending_id -> (email, username, code_id, reg)}
_pending_duck: dict[str, tuple] = {}


# ---------------------------------------------------------------------------
# Account management
# ---------------------------------------------------------------------------

@app.get("/api/accounts", response_model=list[AccountOut])
async def api_list_accounts():
    return await list_accounts()


@app.post("/api/accounts/register", response_model=RegisterResponse)
async def api_register(body: RegisterRequest):
    svc = body.mail_service.lower()

    if svc == "mailtm":
        try:
            reg = FigureLabsRegistration(mail_service=MailTmService())
            data = await asyncio.to_thread(reg.register_auto)
            data["mailService"] = "mailtm"
            saved = await save_account(data)
            return RegisterResponse(done=True, account=AccountOut(**saved))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif svc == "duckmail":
        import uuid as _uuid
        duck = DuckMailService()
        reg = FigureLabsRegistration(mail_service=duck)
        email, username = await asyncio.to_thread(duck.create_account)
        code_id = await asyncio.to_thread(reg.send_verification_code, email)

        pending_id = _uuid.uuid4().hex
        _pending_duck[pending_id] = (email, username, code_id, reg)

        return RegisterResponse(
            done=False,
            pending_id=pending_id,
            email=email,
            inbox_url=f"https://duckmail.sbs/{username}",
        )
    else:
        raise HTTPException(status_code=400, detail="Unknown mail_service")


@app.post("/api/accounts/verify-duckmail", response_model=RegisterResponse)
async def api_verify_duckmail(body: DuckMailVerifyRequest):
    entry = _pending_duck.pop(body.pending_id, None)
    if not entry:
        raise HTTPException(status_code=404, detail="Pending session not found or expired")

    email, username, code_id, reg = entry
    try:
        data = await asyncio.to_thread(reg.login, email, body.code, code_id)
        data["mailService"] = "duckmail"
        data["email"] = email
        saved = await save_account(data)
        return RegisterResponse(done=True, account=AccountOut(**saved))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/accounts/{user_id}")
async def api_delete_account(user_id: str):
    ok = await delete_account(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"ok": True}


@app.patch("/api/accounts/{user_id}/label")
async def api_update_label(user_id: str, body: LabelUpdate):
    await update_label(user_id, body.label)
    return {"ok": True}


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

@app.post("/api/session", response_model=SessionResponse)
async def api_create_session(body: SessionCreate):
    chat = FigureLabsChat(body.access_token)
    sid = await asyncio.to_thread(chat.create_session, body.title)
    if not sid:
        raise HTTPException(status_code=400, detail="Failed to create session")
    return SessionResponse(session_id=sid)


@app.post("/api/message", response_model=MessageResponse)
async def api_send_message(body: MessageSend):
    chat = FigureLabsChat(body.access_token)
    mid = await asyncio.to_thread(
        chat.send_message,
        body.session_id, body.text,
        None, body.model_id, body.ratio, None, True,
    )
    if not mid:
        raise HTTPException(status_code=400, detail="Failed to send message")
    return MessageResponse(message_id=mid)


@app.get("/api/status/{message_id}", response_model=StatusResponse)
async def api_get_status(message_id: str, token: str):
    chat = FigureLabsChat(token)
    st = await asyncio.to_thread(chat.get_message_status, message_id)
    if st is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return StatusResponse(
        status=st.get("status", 0),
        image_model=st.get("imageModel"),
        image_ratio=st.get("imageRatio"),
        file_url=st.get("fileUrl") or [],
    )


@app.post("/api/expand", response_model=ExpandResponse)
async def api_expand(body: ExpandRequest):
    """Expand / enhance a short prompt using the server-side AI."""
    chat = FigureLabsChat(body.access_token)
    expanded = await asyncio.to_thread(chat.expand_prompt, body.message)
    if expanded is None:
        raise HTTPException(status_code=502, detail="Prompt expansion failed")
    return ExpandResponse(expanded=expanded)


# ---------------------------------------------------------------------------
# Download / export
# ---------------------------------------------------------------------------

@app.get("/api/download/{message_id}")
async def api_download(message_id: str, token: str, fmt: str = "png"):
    exp = ExportClient(token)
    urls = await asyncio.to_thread(exp.get_png_urls, message_id)
    if not urls:
        raise HTTPException(status_code=404, detail="Image not ready")

    png_url = urls[0]
    session = make_session(token)
    fmt = fmt.lower()

    if fmt in ("png", "jpg", "jpeg"):
        resp = await asyncio.to_thread(
            lambda: session.get(_PROXY, params={"url": png_url}, stream=True)
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Upstream error")
        media = "image/png" if fmt == "png" else "image/jpeg"
        return Response(
            content=resp.content,
            media_type=media,
            headers={"Content-Disposition": f'attachment; filename="figure.{fmt}"'},
        )

    elif fmt == "svg":
        svg_url = await asyncio.to_thread(_request_svg_url, session, png_url)
        if not svg_url:
            raise HTTPException(status_code=502, detail="SVG conversion failed")
        resp = await asyncio.to_thread(
            lambda: session.get(_PROXY, params={"url": svg_url}, stream=True)
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="SVG fetch failed")
        return Response(
            content=resp.content,
            media_type="image/svg+xml",
            headers={"Content-Disposition": 'attachment; filename="figure.svg"'},
        )

    elif fmt == "pptx":
        data = await asyncio.to_thread(_build_pptx_bytes, session, png_url)
        if data is None:
            raise HTTPException(status_code=502, detail="PPTX build failed")
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": 'attachment; filename="figure.pptx"'},
        )

    raise HTTPException(status_code=400, detail=f"Unknown format: {fmt}")


def _build_pptx_bytes(session, png_s3_url: str) -> Optional[bytes]:
    from ..export.formats import _request_svg_url, _PROXY
    try:
        from pptx import Presentation
        from pptx.util import Emu
        from pptx.oxml.ns import qn
        from lxml import etree
        import zipfile, io
    except ImportError:
        return None

    png_bytes = session.get(_PROXY, params={"url": png_s3_url}, stream=True).content
    svg_url = _request_svg_url(session, png_s3_url)
    if not svg_url:
        return None
    svg_bytes = session.get(_PROXY, params={"url": svg_url}, stream=True).content

    try:
        root = etree.fromstring(svg_bytes)
        parts = root.get("viewBox", "").split()
        svg_w, svg_h = (float(parts[2]), float(parts[3])) if len(parts) == 4 else (1376.0, 768.0)
    except Exception:
        svg_w, svg_h = 1376.0, 768.0

    prs = Presentation()
    slide_w = Emu(9144000)
    slide_h = Emu(int(slide_w * svg_h / svg_w))
    prs.slide_width, prs.slide_height = slide_w, slide_h
    prs.slides.add_slide(prs.slide_layouts[6])

    buf = io.BytesIO(); prs.save(buf); buf.seek(0)

    _REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
    _IMG_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
    _A_NS  = "http://schemas.openxmlformats.org/drawingml/2006/main"
    _P_NS  = "http://schemas.openxmlformats.org/presentationml/2006/main"
    _R_NS  = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    _ASVG  = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
    _EXT   = "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"

    out = io.BytesIO()
    s_xml, rels, ct = "ppt/slides/slide1.xml", "ppt/slides/_rels/slide1.xml.rels", "[Content_Types].xml"
    rewritten = {s_xml, rels, ct}

    with zipfile.ZipFile(buf, "r") as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename not in rewritten:
                zout.writestr(item, zin.read(item.filename))
        zout.writestr("ppt/media/image1.png", png_bytes)
        zout.writestr("ppt/media/image2.svg", svg_bytes)

        tree = etree.fromstring(zin.read(s_xml))
        spTree = tree.find(".//" + qn("p:spTree"))
        pic = (
            f'<p:pic xmlns:p="{_P_NS}" xmlns:a="{_A_NS}" xmlns:r="{_R_NS}" xmlns:asvg="{_ASVG}">'
            f'<p:nvPicPr><p:cNvPr id="2" name="Figure"/>'
            f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="rId1"><a:extLst><a:ext uri="{_EXT}">'
            f'<asvg:svgBlip r:embed="rId2"/></a:ext></a:extLst></a:blip>'
            f'<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="0" y="0"/>'
            f'<a:ext cx="{int(slide_w)}" cy="{int(slide_h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
        )
        spTree.append(etree.fromstring(pic))
        zout.writestr(s_xml, etree.tostring(tree, xml_declaration=True, encoding="UTF-8", standalone=True))

        try:
            rt = etree.fromstring(zin.read(rels))
        except KeyError:
            rt = etree.fromstring(b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
        for rid, tgt in [("rId1", "../media/image1.png"), ("rId2", "../media/image2.svg")]:
            r = etree.SubElement(rt, f"{{{_REL_NS}}}Relationship")
            r.set("Id", rid); r.set("Type", _IMG_TYPE); r.set("Target", tgt)
        zout.writestr(rels, etree.tostring(rt, xml_declaration=True, encoding="UTF-8", standalone=True))

        ct_tree = etree.fromstring(zin.read(ct))
        ct_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
        existing = {e.get("Extension") for e in ct_tree.findall(f"{{{ct_ns}}}Default")}
        for ext, ctype in [("svg", "image/svg+xml"), ("png", "image/png")]:
            if ext not in existing:
                el = etree.SubElement(ct_tree, f"{{{ct_ns}}}Default")
                el.set("Extension", ext); el.set("ContentType", ctype)
        zout.writestr(ct, etree.tostring(ct_tree, xml_declaration=True, encoding="UTF-8", standalone=True))

    return out.getvalue()


# ---------------------------------------------------------------------------
# Statistics API (新增)
# ---------------------------------------------------------------------------

class StatsResponse(BaseModel):
    labels: list[str]
    total_requests: list[int]
    failed_requests: list[int]
    rate_limited_requests: list[int]
    model_requests: dict[str, list[int]]
    model_ttfb_times: dict[str, list[float]]
    model_total_times: dict[str, list[float]]


class TotalCountsResponse(BaseModel):
    success: int
    failed: int


@app.get("/api/stats", response_model=StatsResponse)
async def api_get_stats(time_range: str = "24h"):
    """Get aggregated statistics by time range (24h/7d/30d)."""
    if time_range not in ("24h", "7d", "30d"):
        raise HTTPException(status_code=400, detail="Invalid time_range. Use 24h, 7d, or 30d")

    stats = await stats_db.get_stats_by_time_range(time_range)
    return StatsResponse(**stats)


@app.get("/api/stats/totals", response_model=TotalCountsResponse)
async def api_get_total_counts():
    """Get total success and failed request counts."""
    success, failed = await stats_db.get_total_counts()
    return TotalCountsResponse(success=success, failed=failed)


# ---------------------------------------------------------------------------
# Static frontend
# ---------------------------------------------------------------------------

_STATIC = Path(__file__).parent.parent.parent / "frontend" / "dist"
if _STATIC.exists():
    app.mount("/", StaticFiles(directory=str(_STATIC), html=True), name="static")
