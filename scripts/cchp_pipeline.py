"""Full pipeline: register → generate CCHP diagram → export PNG + SVG + PPTX."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.register import FigureLabsRegistration, MailTmService
from src.chat import FigureLabsChat
from src.export import ExportClient

PROMPT = (
    "Generate a professional CCHP (Combined Cooling, Heating and Power) system schematic diagram. "
    "Show left-to-right energy flow with labeled components: natural gas input to Gas Turbine, "
    "electricity output to building loads and grid, exhaust heat to HRSG (waste heat recovery), "
    "absorption chiller producing cooling output, heat exchanger for space heating and hot water, "
    "auxiliary boiler as backup, thermal energy storage tank. "
    "Use color-coded arrows: red=heat, blue=cooling, yellow=electricity, grey=fuel. "
    "Add efficiency annotations. White background. Title: CCHP System Schematic. "
    "Style: academic flat, 16:9."
)

OUTPUT_DIR = "./output/cchp"
LOG_FILE = "./output/cchp/_run.log"


def log(msg, fh=None):
    print(msg)
    if fh:
        fh.write(msg + "\n")
        fh.flush()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fh = open(LOG_FILE, "w", buffering=1)

    log("=" * 60, fh)
    log("CCHP Diagram: Register → Generate → Export", fh)
    log("=" * 60, fh)

    # ── 1. Register new account ──────────────────────────────────
    log("\n[1/5] Registering new account via Mail.tm", fh)
    reg = FigureLabsRegistration(mail_service=MailTmService())
    try:
        data = reg.register_auto()
    except Exception as e:
        log(f"Registration failed: {e}", fh)
        fh.close()
        return 1

    token = data["accessToken"]
    log(f"  User:  {data['userId']}", fh)
    log(f"  Email: {data.get('email', 'n/a')}", fh)
    log(f"  Token: {token[:20]}...", fh)

    with open(f"{OUTPUT_DIR}/_token.txt", "w") as f:
        f.write(token)

    # ── 2. Login check ───────────────────────────────────────────
    log("\n[2/5] Verifying login", fh)
    chat = FigureLabsChat(token)
    if not chat.check_login():
        log("Login check failed", fh)
        fh.close()
        return 1
    log("  Login OK", fh)

    # ── 3. Send generation prompt ────────────────────────────────
    log("\n[3/5] Sending CCHP prompt", fh)
    session_id = chat.create_session(title="CCHP System Schematic")
    if not session_id:
        log("Failed to create session", fh)
        fh.close()
        return 1

    message_id = chat.send_message(
        session_id,
        PROMPT,
        model_id=7,
        ratio="16:9",
        style="Flat",
        first_message=True,
    )
    if not message_id:
        log("Failed to send message", fh)
        fh.close()
        return 1

    log(f"  Session:  https://chat.figurelabs.ai/project/{session_id}", fh)
    log(f"  Message:  {message_id}", fh)

    json.dump({"session_id": session_id, "message_id": message_id, "token": token},
              open(f"{OUTPUT_DIR}/_state.json", "w"), indent=2)

    # ── 4. Wait for generation ───────────────────────────────────
    log("\n[4/5] Waiting for generation (up to 3 min)", fh)
    status = chat.wait_for_completion(message_id, timeout=180)
    if not status:
        log("Generation failed or timed out", fh)
        fh.close()
        return 1

    log(f"  Model: {status.get('imageModel')}  Ratio: {status.get('imageRatio')}", fh)

    # ── 5. Export PNG + SVG + PPTX ───────────────────────────────
    log("\n[5/5] Exporting", fh)
    exp = ExportClient(token)

    png  = exp.download(message_id, fmt="png",  output_dir=OUTPUT_DIR, filename="cchp")
    svg  = exp.download(message_id, fmt="svg",  output_dir=OUTPUT_DIR, filename="cchp")
    pptx = exp.download(message_id, fmt="pptx", output_dir=OUTPUT_DIR, filename="cchp")

    log(f"\n  PNG:  {png}", fh)
    log(f"  SVG:  {svg}", fh)
    log(f"  PPTX: {pptx}", fh)

    ok = all(p is not None for p in [png, svg, pptx])
    log(f"\n{'All exports succeeded' if ok else 'Some exports failed'}", fh)
    log("=" * 60, fh)

    fh.close()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
