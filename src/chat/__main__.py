"""CLI entry point for the chat module."""

import argparse
import sys

from src.chat import FigureLabsChat


def main() -> int:
    parser = argparse.ArgumentParser(description="FigureLabs.ai chat client")
    parser.add_argument("token", help="Access token")
    sub = parser.add_subparsers(dest="cmd")

    gen = sub.add_parser("generate", aliases=["gen"], help="Generate a new figure")
    gen.add_argument("--message", "-m", default="Hello!", help="Prompt text")
    gen.add_argument("--title", default="CLI Chat", help="Session title")
    gen.add_argument("--model", type=int, help="Model ID (6/7/10/12)")
    gen.add_argument("--ratio", help="Image ratio (16:9, 1:1, ...)")
    gen.add_argument("--style", help="Style (Flat, 3D, ...)")
    gen.add_argument("--wait", action="store_true", help="Wait for completion")

    args = parser.parse_args()

    client = FigureLabsChat(args.token)
    if not client.check_login():
        print("Login failed")
        return 1

    if args.cmd in ("generate", "gen"):
        session_id = client.create_session(title=args.title)
        if not session_id:
            return 1
        message_id = client.send_message(
            session_id,
            args.message,
            model_id=args.model,
            ratio=args.ratio,
            style=args.style,
            first_message=True,
        )
        if not message_id:
            return 1
        print(f"Session: https://chat.figurelabs.ai/project/{session_id}")
        if args.wait:
            status = client.wait_for_completion(message_id)
            if status:
                urls = status.get("fileUrl", [])
                if urls:
                    print(f"Image: {urls[0][:100]}...")
        else:
            print(f"Use `python -m src.export {args.token} {message_id}` to download")
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
