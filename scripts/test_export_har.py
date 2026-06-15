"""Quick PPTX export test using the token and PNG URL from the captured HAR."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json, urllib.parse
from src.export._session import make_session
from src.export import formats

HAR_PATH = "01HttpArchive/chat.figurelabs.ai_2026_06_15_21_40_52.har"

with open(HAR_PATH, encoding="utf-8") as f:
    har = json.load(f)

e0 = har["log"]["entries"][0]
url = e0["request"]["url"]
qs = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
PNG_S3_URL = urllib.parse.unquote(qs["url"][0])

cookie_hdrs = [h["value"] for h in e0["request"]["headers"]
               if h["name"].lower() == "cookie" and "Access-Token" in h["value"]]
TOKEN = cookie_hdrs[0].split("Access-Token=")[1].split(";")[0].strip()

print(f"Token: {TOKEN[:16]}...")
print(f"S3 URL: {PNG_S3_URL[:80]}...")

session = make_session(TOKEN)

print("\n[png]")
png = formats.download_png(session, PNG_S3_URL, output_dir="output", filename="har_test")
print("->", png)

print("\n[svg]")
svg = formats.download_svg(session, PNG_S3_URL, output_dir="output", filename="har_test")
print("->", svg)

print("\n[pptx]")
pptx = formats.download_pptx(session, PNG_S3_URL, output_dir="output", filename="har_test")
print("->", pptx)
