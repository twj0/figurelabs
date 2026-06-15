"""CLI entry point for registration."""

import argparse
import sys

from src.register import DuckMailService, FigureLabsRegistration, MailTmService


def main():
    parser = argparse.ArgumentParser(
        description="FigureLabs.ai automated registration tool"
    )
    parser.add_argument(
        "--service",
        choices=["mailtm", "duckmail"],
        default="mailtm",
        help="Email service (default: mailtm)",
    )
    parser.add_argument(
        "--email",
        type=str,
        help="Email address (optional, generated if not provided)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("FigureLabs.ai Registration Tool")
    print("=" * 60)

    # Select mail service
    if args.service == "mailtm":
        print("\nUsing Mail.tm (automated)...")
        mail_service = MailTmService()
        auto_mode = True
    else:
        print("\nUsing DuckMail (manual verification)...")
        mail_service = DuckMailService()
        auto_mode = False

    # Create client
    client = FigureLabsRegistration(mail_service)

    try:
        if auto_mode:
            result = client.register_auto()
        else:
            result = client.register_manual(email=args.email)

        print("\n✅ Registration successful!")
        return 0

    except Exception as e:
        print(f"\n❌ Registration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
