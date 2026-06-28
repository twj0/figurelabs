from fastapi.testclient import TestClient

from src.api import app as app_module


class FakeFigureLabsChat:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def create_session(self, title: str = "Chat Session", agent_id: int = 0):
        assert self.access_token == "figure-token"
        return "session-1"

    def send_message(
        self,
        session_id: str,
        message: str,
        action_type: str = "NORMAL_CHAT",
        model_id=None,
        ratio=None,
        style=None,
        first_message: bool = False,
        scene: str = "normal_chat",
    ):
        assert session_id == "session-1"
        assert message == "Draw a process diagram"
        assert model_id == 7
        assert ratio == "16:9"
        assert first_message is True
        assert scene == "gen-svg"
        return "message-1"

    def wait_for_completion(self, message_id: str, timeout: int = 180, poll_interval: int = 3):
        assert message_id == "message-1"
        return {"status": 1, "fileUrl": ["https://example.test/figure.png"]}


def test_openai_models_lists_figurelabs_models():
    with TestClient(app_module.app) as client:
        response = client.get("/v1/models")

    assert response.status_code == 200
    model_ids = {model["id"] for model in response.json()["data"]}
    assert "figurelabs-nano-banana-pro" in model_ids


def test_openai_chat_completion_returns_openai_shape(monkeypatch):
    monkeypatch.setattr(app_module, "FigureLabsChat", FakeFigureLabsChat)

    with TestClient(app_module.app) as client:
        response = client.post(
            "/v1/chat/completions",
            headers={"Authorization": "Bearer figure-token"},
            json={
                "model": "figurelabs-nano-banana-pro",
                "messages": [{"role": "user", "content": "Draw a process diagram"}],
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert data["model"] == "figurelabs-nano-banana-pro"
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert "https://example.test/figure.png" in data["choices"][0]["message"]["content"]


def test_openai_chat_completion_streams_openai_chunks(monkeypatch):
    monkeypatch.setattr(app_module, "FigureLabsChat", FakeFigureLabsChat)

    with TestClient(app_module.app) as client:
        response = client.post(
            "/v1/chat/completions",
            headers={"Authorization": "Bearer figure-token"},
            json={
                "model": "figurelabs-nano-banana-pro",
                "messages": [{"role": "user", "content": "Draw a process diagram"}],
                "stream": True,
            },
        )

    assert response.status_code == 200
    assert "chat.completion.chunk" in response.text
    assert "https://example.test/figure.png" in response.text
    assert "data: [DONE]" in response.text


def test_openai_chat_completion_requires_authorization():
    with TestClient(app_module.app) as client:
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "figurelabs-nano-banana-pro",
                "messages": [{"role": "user", "content": "Draw a process diagram"}],
            },
        )

    assert response.status_code == 401
