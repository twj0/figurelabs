"""Probe export endpoints with a fresh token.

Steps:
    1. Generate image with new token
    2. Try SVG conversion (known endpoint)
    3. Probe possible PPTX endpoints
    4. Download whatever succeeds

Run: python scripts/probe_export.py
"""

import json, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import requests
from src.chat import FigureLabsChat
from src.export import ExportClient
from src.export._session import make_session

TOKEN2 = open("output/_token2.txt").read().strip()

PROMPT = (
    "Generate a professional IEEE 33-bus radial distribution power grid scheduling diagram. "
    "Centralized radial topology, utility substation at center, 33 numbered bus nodes, "
    "solar PV and wind icons, teal BESS icon near terminal node, voltage profile overlay. "
    "Label: IEEE 33-Bus Microgrid Dispatch. Style: academic flat, 16:9."
)

chat = FigureLabsChat(TOKEN2)
assert chat.check_login(), "login failed"

session_id = chat.create_session(title="IEEE33 probe")
message_id = chat.send_message(session_id, PROMPT, ratio="16:9", style="Flat", first_message=True)
print(f"session={session_id}  message={message_id}")

status = chat.wait_for_completion(message_id, timeout=180)
assert status, "generation failed"
png_url = status["fileUrl"][0]
print(f"png_url={png_url[:80]}...")

# Check remaining points
s = make_session(TOKEN2)
pts = s.post("https://chat.figurelabs.ai/app-api/plot/package/points/remaining", json={}).json()
print(f"points: {pts['data']}")

# PNG baseline
exp = ExportClient(TOKEN2)
png = exp.download(message_id, fmt="png", output_dir="output", filename="ieee33_probe")
print(f"PNG: {png}")

# SVG
svg = exp.download(message_id, fmt="svg", output_dir="output", filename="ieee33_probe")
print(f"SVG: {svg}")

# Probe PPTX — try known patterns
BASE = "https://chat.figurelabs.ai"
candidates = [
    f"{BASE}/app-api/plot/image/pptx",
    f"{BASE}/app-api/plot/chat/export/pptx",
    f"{BASE}/app-api/plot/export/pptx",
    f"{BASE}/app-api/plot/image/export/pptx",
]

print("\nProbing PPTX endpoints:")
for ep in candidates:
    r = s.post(ep, json={"imageUrl": [png_url]})
    print(f"  POST {ep.split('plot/')[1]}  -> HTTP {r.status_code}  body={r.text[:120]}")

# Also try with messageId payload
ep_msg = f"{BASE}/app-api/plot/image/pptx"
r2 = s.post(ep_msg, json={"messageId": message_id})
print(f"  POST image/pptx (messageId) -> HTTP {r2.status_code}  body={r2.text[:120]}")

r3 = s.post(ep_msg, json={"sourceId": message_id})
print(f"  POST image/pptx (sourceId)  -> HTTP {r3.status_code}  body={r3.text[:120]}")
