# 第3回 解答

## 演習

* 第1回（素のLLM）とエージェントの回答の違い：素のLLMは講座固有の知識を持たずハルシネーションを起こしやすいが、エージェントは自律的にツールを使って外部情報を検索するため、正確な事実に基づいた回答ができる。
* `--trace` で見えたツール呼び出し（ツール名と引数）：ツール名 `make_quiz`、引数 `{'lecture': 2}`
* 1つの質問での LLM 呼び出し回数（`requests`）：2回
* 追加したツールと、docstring に書いた説明：ツール `make_quiz`。説明：「指定した回の用語から 1つを選び、確認問題と答えを返す。『第2回の確認問題を出して』のように、復習用の問題を求められたときに使う。」

## 宿題

- 取り組んだレベル： 実装 
- 取り組んだレベル： 実装

- やったこと：
  - `app/tools.py` に、学習記録を `learning_log/` フォルダに保存するツール `save_learning_log` を実装した。
  - ファイル保存は取り消しにくい操作であるため、`app/agent.py` でツールを登録する際に `requires_approval=True` を指定し、利用者の確認を挟むようにした。
  - エージェントの `output_type` に `DeferredToolRequests` を追加し、CLIでの実行時に承認待ちで処理が一時停止し、ユーザーが許可 (y) を出した場合に続きが実行される仕組みを構築した。
  - 実行時、APIの混雑（503エラー）が発生したため、コマンド先頭に `AIE_MODEL=gemini-3.1-flash-lite` を指定してモデルを切り替えて検証を行った。

- 結果：
  エージェントに保存を指示したところ、即座にツールが実行されるのではなく、ターミナル上で `learning_log/ に保存しますか？ [y/N]:` と承認を求められ、処理が一時停止した。`y` を入力して承認するとツールが実行され、ファイルが生成された。

  【実行時のトレースログ】
  ```text
  [save_learning_log] 保存内容:
  {
    "content": "エージェントのツール呼び出しと承認プロセス（Human-in-the-loop）について学習。"
  }
  learning_log/ に保存しますか？ [y/N]: y
  学習記録の保存が完了いたしました。

  保存内容：エージェントのツール呼び出しと承認プロセス（Human-in-the-loop）について学習。
  保存先：learning_log/20261105-094703-501281.md

  （参考：第3回）

  --- trace ---
  [tool call]   save_learning_log({'content': 'エージェントのツール呼び出しと承認プロセス（Human-in-the-loop）について学習。'})
  [tool return] save_learning_log -> 学習記録を保存しました: learning_log/20261105-094703-501281.md…
  [usage] RunUsage(cost=Decimal('0.0002735'), details={'text_prompt_tokens': 650}, input_text_tokens=650, input_tokens=650, output_tokens=74, requests=1, tool_calls=1)
