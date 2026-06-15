"""One-shot: send prompt, wait, download PNG+SVG+PPTX.

Usage:
    uv run python scripts/generate_and_export.py <token> <session_id> <message_id>
    uv run python scripts/generate_and_export.py <token>   # send fresh prompt
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.chat import FigureLabsChat
from src.export import ExportClient

PROMPT = (
    "Generate a professional IEEE 33-bus radial distribution power grid scheduling diagram. "
    "Layout: centralized radial topology, utility substation at center, 33 numbered circular "
    "bus nodes connected by dark-grey lines. Include minimalist icons for solar PV, wind "
    "turbines, and loads along branches. Add a teal battery energy storage system (BESS) icon "
    "near the terminal node. Overlay a dual-curve voltage profile plot showing uncontrolled "
    "stress below 0.95 p.u. (red dashed) and optimized dispatch above 0.95 p.u. (green solid). "
    "Top-left label: IEEE 33-Bus Microgrid Dispatch. Style: academic flat, 16:9 ratio."
)

OUTPUT_DIR = "./output"
STATE_FILE = "./output/_state.json"


def load_state():
    try:
        return json.load(open(STATE_FILE))
    except Exception:
        return {}


def save_state(d):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json.dump(d, open(STATE_FILE, "w"), indent=2)


def main():
    token = sys.argv[1] if len(sys.argv) > 1 else open("output/_token.txt").read().strip()
    chat = FigureLabsChat(token)

    if not chat.check_login():
        print("Login failed")
        return 1

    state = load_state()

    # Re-use existing message_id if available and not yet complete
    message_id = state.get("message_id")
    if not message_id:
        session_id = chat.create_session(title="IEEE 33-Bus Microgrid Dispatch")
        if not session_id:
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
            return 1

        save_state({"session_id": session_id, "message_id": message_id, "token": token})
        print(f"Session: https://chat.figurelabs.ai/project/{session_id}")
    else:
        print(f"Resuming message_id={message_id}")

    status = chat.wait_for_completion(message_id, timeout=180)
    if not status:
        print("Generation failed or timed out")
        return 1

    print(f"Model: {status.get('imageModel')}  Ratio: {status.get('imageRatio')}")

    exp = ExportClient(token)

    png = exp.download(message_id, fmt="png", output_dir=OUTPUT_DIR, filename="ieee33_microgrid")
    svg = exp.download(message_id, fmt="svg", output_dir=OUTPUT_DIR, filename="ieee33_microgrid")
    pptx = exp.download(message_id, fmt="pptx", output_dir=OUTPUT_DIR, filename="ieee33_microgrid")

    print("\nResults:")
    print(f"  PNG:  {png}")
    print(f"  SVG:  {svg}")
    print(f"  PPTX: {pptx}")

    save_state({
        **state,
        "png": png,
        "svg": svg,
        "pptx": pptx,
        "done": True,
    })
    return 0 if png else 1


if __name__ == "__main__":
    sys.exit(main())
