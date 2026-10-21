"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask --interactive "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

--interactive を指定すると、空行を入力するまで会話履歴を保って質問できる。
ツールを持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import types
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str, history: list[types.Content] | None = None) -> str:
    if history is None:
        history = []
    history.append(
        types.Content(role="user", parts=[types.Part.from_text(text=question)])
    )

    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=history)
    if not response.candidates or response.candidates[0].content is None:
        raise RuntimeError("モデルから応答がありませんでした")
    history.append(response.candidates[0].content)

    usage_metadata = response.usage_metadata
    prompt_token_count = (
        usage_metadata.prompt_token_count if usage_metadata is not None else None
    )
    candidates_token_count = (
        usage_metadata.candidates_token_count if usage_metadata is not None else None
    )
    print(
        "[入力トークン数] "
        f"{prompt_token_count if prompt_token_count is not None else '取得できませんでした'}"
    )
    print(
        "[出力トークン数] "
        f"{candidates_token_count if candidates_token_count is not None else '取得できませんでした'}"
    )

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="空行を入力するまで会話履歴を保って続けて質問する",
    )
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    history: list[types.Content] = []
    question = args.question
    try:
        while True:
            print(f"[質問] {question}\n")
            print(ask(question, history))
            if not args.interactive:
                break
            try:
                question = input("\n続けて質問してください（空行で終了）: ").strip()
            except EOFError:
                break
            if not question:
                break
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
