---
description: 指定した話数の新規1話を、設計確認から検証・正典更新まで完遂する
argument-hint: <話数>（例: 12 / ep12 / 第12話。複数話は「12-15」）
---

新しい本文の執筆依頼です。`long-novel-orchestrator` スキルを入口として起動し、対象話数「$ARGUMENTS」を書いてください。

- 入口は必ず `long-novel-orchestrator`。内部で `write-episode` を1話ずつ呼び出し、適切な文体スキルを使う。
- `CLAUDE.md` の完了の定義（本文保存・`scripts/check.sh --strict` ゼロ・視点/キャラ/情報格差/時系列の照合・`ai-novel-detector` 診断・状態台帳更新・再検査）をすべて満たすまで「完成」と報告しない。
- 話数指定がなければ、続きの話を `work/continuity/current-state.md` から特定して確認する。
