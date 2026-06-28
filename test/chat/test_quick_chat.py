"""Quick chat test - validates message submission without waiting for full response."""

import sys

from src.chat import FigureLabsChat


def run_quick_chat(access_token: str) -> bool:
    """Quick chat test without waiting for AI generation.

    Args:
        access_token: Access token

    Returns:
        True if message submission succeeds, False otherwise
    """
    print("=" * 60)
    print("FigureLabs.ai Quick Chat Test")
    print("=" * 60)

    client = FigureLabsChat(access_token)

    # Create session
    print("\n[1/2] Creating session...")
    session_id = client.create_session(title="Quick Test")

    if not session_id:
        print("❌ Failed to create session")
        return False

    print(f"✓ Session created: {session_id}")

    # Send message
    print("\n[2/2] Sending test message...")
    message_id = client.send_message(session_id, "Generate a simple flowchart diagram.")

    if not message_id:
        print("❌ Failed to send message")
        return False

    print(f"✓ Message sent: {message_id}")

    print("\n" + "=" * 60)
    print("✅ Chat test passed!")
    print("=" * 60)
    print("\nNotes:")
    print("- Session creation successful")
    print("- Message submission successful")
    print("- Full AI response requires 30-90 seconds")
    print(f"- View result at: https://chat.figurelabs.ai/project/{session_id}")

    return True


if __name__ == "__main__":
    # Test token
    test_token = "2a2d514100904fa884edc20b3927fff3"

    if len(sys.argv) > 1:
        test_token = sys.argv[1]

    print(f"Token: {test_token[:20]}...\n")

    success = run_quick_chat(test_token)
    sys.exit(0 if success else 1)
