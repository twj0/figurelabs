# FigureLabs.ai Python Client

## Quick Start

### 1. Register Account

```python
from src.register import FigureLabsRegistration, MailTmService

# Automated registration with Mail.tm
mail_service = MailTmService()
client = FigureLabsRegistration(mail_service)
result = client.register_auto()

print(f"User ID: {result['userId']}")
print(f"Access Token: {result['accessToken']}")
```

### 2. Chat

```python
from src.chat import FigureLabsChat

# Initialize chat client
chat = FigureLabsChat(access_token="your_token_here")

# Create session
session_id = chat.create_session(title="My Project")

# Send message
message_id = chat.send_message(session_id, "Generate a flowchart")

# Visit web UI to view result
print(f"https://chat.figurelabs.ai/project/{session_id}")
```

## Testing

```bash
# Test automated registration
python test/register/test_mailtm.py

# Test token verification
python test/register/test_token.py <token>

# Test quick chat (message submission only)
python test/chat/test_quick_chat.py <token>

# Test full chat (wait for AI response)
python test/chat/test_full_chat.py <token>
```

## Core API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/app-api/plot/member/mail` | POST | Send verification code |
| `/app-api/plot/member/login` | POST | Register/Login |
| `/app-api/plot/member/info` | GET | User information |
| `/app-api/plot/chat/session/create` | POST | Create chat session |
| `/app-api/plot/chat/message` | POST | Send message |
| `/app-api/plot/chat/message/status` | GET | Query message status |

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests
pytest

# Format code
black src/ test/

# Lint
ruff check src/ test/
```

#
