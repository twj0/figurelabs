"""Test advanced chat features (model selection, style control)."""

import sys

from src.chat import FigureLabsChatExtended


def test_advanced_chat(access_token: str) -> bool:
    """Test advanced chat features with model and style parameters.

    Args:
        access_token: Access token

    Returns:
        True if test passes, False otherwise
    """
    print("=" * 80)
    print("FigureLabs.ai Advanced Chat Test")
    print("=" * 80)

    client = FigureLabsChatExtended(access_token)

    # 1. Get available models
    print("\n[1/4] Fetching available models...")
    models = client.get_available_models(scene="iiterature")

    if models:
        print(f"\nFound {len(models)} models:")
        for i, model in enumerate(models[:5], 1):
            print(f"  {i}. {model.get('name', 'Unknown')} (ID: {model.get('id', 'N/A')})")
    else:
        print("⚠️ Could not fetch models, using default")

    # 2. Get session history
    print("\n[2/4] Fetching session history...")
    history = client.get_session_history(page=1, page_size=5)

    if history:
        print(f"\nTotal sessions: {history.get('total', 0)}")
        sessions = history.get('list', [])
        for session in sessions[:3]:
            print(f"  - {session.get('title', 'Untitled')[:50]}...")
    else:
        print("⚠️ No history found or query failed")

    # 3. Create new session
    print("\n[3/4] Creating new session...")
    from src.chat import FigureLabsChat

    basic_client = FigureLabsChat(access_token)
    session_id = basic_client.create_session(title="Advanced Features Test")

    if not session_id:
        print("❌ Failed to create session")
        return False

    # 4. Send advanced message
    print("\n[4/4] Sending message with advanced parameters...")

    message_id = client.send_message_advanced(
        session_id=session_id,
        text="Generate a simple block diagram showing client-server architecture.",
        model_id=7,  # Nano Banana Pro
        ratio="16:9",
        style="Flat",
        first_message=True,
    )

    if not message_id:
        print("❌ Failed to send message")
        return False

    print(f"\n✅ Message sent successfully!")
    print(f"Session URL: https://chat.figurelabs.ai/project/{session_id}")

    # 5. Check thinking status (optional)
    print("\n[Optional] Checking thinking status...")
    thinking_status = client.get_thinking_status(message_id)

    if thinking_status:
        print(f"  Status: {thinking_status.get('status')}")
        print(f"  Progress: {thinking_status.get('currentStep')}/{thinking_status.get('totalSteps')}")
        print(f"  Step: {thinking_status.get('stepName')}")
    else:
        print("  No thinking status available (may not be applicable for this model)")

    print("\n" + "=" * 80)
    print("✅ Advanced chat test passed!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    # Test token
    test_token = "2a2d514100904fa884edc20b3927fff3"

    if len(sys.argv) > 1:
        test_token = sys.argv[1]

    print(f"Using token: {test_token[:20]}...\n")

    success = test_advanced_chat(test_token)
    sys.exit(0 if success else 1)
