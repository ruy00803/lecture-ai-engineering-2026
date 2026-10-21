from types import SimpleNamespace

from google.genai import types

from app import ask


def test_ask_passes_previous_turns_to_the_next_request(monkeypatch):
    requests = []

    class FakeModels:
        def generate_content(self, *, model, contents):
            assert model == ask.MODEL
            requests.append(list(contents))
            answer = f"回答{len(requests)}"
            return SimpleNamespace(
                text=answer,
                candidates=[
                    SimpleNamespace(
                        content=types.Content(
                            role="model",
                            parts=[types.Part.from_text(text=answer)],
                        )
                    )
                ],
                usage_metadata=None,
            )

    class FakeClient:
        def __init__(self, *, api_key):
            assert api_key == "test-key"
            self.models = FakeModels()

    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(ask.genai, "Client", FakeClient)
    history = []

    assert ask.ask("最初の質問", history) == "回答1"
    assert ask.ask("続けて質問", history) == "回答2"

    assert [
        (message.role, message.parts[0].text) for message in requests[1]
    ] == [
        ("user", "最初の質問"),
        ("model", "回答1"),
        ("user", "続けて質問"),
    ]
