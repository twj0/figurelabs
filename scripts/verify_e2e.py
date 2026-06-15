"""End-to-end verification: register → chat → generate → export PPTX.

Steps:
    1. Auto-register via Mail.tm
    2. Create a chat session
    3. Send IEEE 33-bus microgrid scheduling diagram prompt
    4. Poll until generation completes
    5. Download PNG (baseline check)
    6. Download PPTX to ./output/

Run:
    uv run python scripts/verify_e2e.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.register import FigureLabsRegistration, MailTmService
from src.chat import FigureLabsChat
from src.export import ExportClient

PROMPT = (
    "Generate a professional IEEE 33-bus radial distribution power grid scheduling diagram. "
    "Layout: centralized radial topology, utility substation at center, 33 numbered circular "
    "bus nodes connected by dark-grey lines. Include minimalist icons for solar PV, wind "
    "turbines, and loads along branches. Add a teal battery energy storage system (BESS) icon "
    "near the terminal node. Overlay a dual-curve voltage profile plot showing uncontrolled "
    "stress below 0.95 p.u. (red dashed) and optimized dispatch above 0.95 p.u. (green solid). "
    "Top-left label: 'IEEE 33-Bus Microgrid Dispatch'. Style: academic flat, 16:9 ratio."
)

OUTPUT_DIR = "./output"


def main() -> int:
    print("=" * 60)
    print("FigureLabs.ai End-to-End Verification")
    print("=" * 60)

    # ── Step 1: Register ────────────────────────────────────────
    print("\n[Step 1] Auto-register via Mail.tm")
    reg = FigureLabsRegistration(mail_service=MailTmService())
    try:
        data = reg.register_auto()
    except Exception as e:
        print(f"Registration failed: {e}")
        return 1

    token = data["accessToken"]
    print(f"Token: {token[:20]}...")

    # ── Step 2: Create session ──────────────────────────────────
    print("\n[Step 2] Create chat session")
    chat = FigureLabsChat(token)
    if not chat.check_login():
        print("Login check failed")
        return 1

    session_id = chat.create_session(title="IEEE 33-Bus Microgrid Dispatch")
    if not session_id:
        print("Failed to create session")
        return 1

    # ── Step 3: Send prompt ─────────────────────────────────────
    print("\n[Step 3] Send generation prompt")
    message_id = chat.send_message(
        session_id,
        PROMPT,
        model_id=7,       # Nano Banana Pro — 30s
        ratio="16:9",
        style="Flat",
        first_message=True,
    )
    if not message_id:
        print("Failed to send message")
        return 1

    # ── Step 4: Wait for completion ─────────────────────────────
    print("\n[Step 4] Wait for generation (up to 3 min)")
    status = chat.wait_for_completion(message_id, timeout=180)
    if not status:
        print("Generation failed or timed out")
        return 1

    png_urls = status.get("fileUrl", [])
    print(f"Generated: {len(png_urls)} file(s)")
    print(f"Model: {status.get('imageModel')}  Ratio: {status.get('imageRatio')}")

    # ── Step 5: Download PNG (baseline) ────────────────────────
    print("\n[Step 5] Download PNG")
    exp = ExportClient(token)
    png_path = exp.download(message_id, fmt="png", output_dir=OUTPUT_DIR, filename="ieee33_microgrid")
    if not png_path:
        print("PNG download failed")
        return 1

    # ── Step 6: Download PPTX ───────────────────────────────────
    print("\n[Step 6] Download PPTX")
    pptx_path = exp.download(message_id, fmt="pptx", output_dir=OUTPUT_DIR, filename="ieee33_microgrid")
    if not pptx_path:
        print("PPTX download failed — endpoint may need HAR verification")
        print(f"PNG is available at: {png_path}")
        return 1

    print("\n" + "=" * 60)
    print("Verification complete")
    print(f"  PNG:  {png_path}")
    print(f"  PPTX: {pptx_path}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
