# クレジット

このリポジトリは、次の方々の公開物を土台にしている。各項目に、作者、出典、取得時点、利用条件、こちらでの扱いを記す。
原本はすべて `vendor/`（コミット固定）に置き、`sets/` と `templates/` にあるのは、そこから取り出したものである。

## Lauren Tan — pstack（cursor/plugins）

- 出典: https://github.com/cursor/plugins/tree/main/pstack （commit 93b00b89ef425a9c1bac0d0b317dfc49c930ac99、2026-09-05 取得）
- 利用条件: MIT License（`pstack/LICENSE`）
- こちらでの扱い:
  - `sets/engineering/architect`: `skills/architect` を基に、Cursor 固有の参照（`how` / `why` / `arena` / `interrogate` スキル、モデル固定）を差し替え、既定を「設計書で止まる」に変えた。`principle-*` 21本は `references/principles/` に frontmatter を外して同梱
  - `sets/engineering/verify-and-fix`: `skills/tdd` を基に、名前と発火条件を広げ、「done と言う前」の3行を足した
  - `sets/engineering/tech-writing-ja`: `skills/technical-writing` を基に、`unslop` を `references/unslop.md` として同梱し、日本語の節を足した
- 原本: `vendor/cursor__plugins/pstack/`

## Matt Pocock — mattpocock/skills

- 出典: https://github.com/mattpocock/skills （commit 3cca18b368ae95cdbdebbff572ccafa662551015、2026-09-05 取得）
- 利用条件: MIT License
- こちらでの扱い: `sets/engineering/grilling` と `grill-me` は原文のまま。frontmatter に出典を追記しただけ。`skills/in-progress/writing-*` は参考として `vendor/` にのみ置く
- 原本: `vendor/mattpocock__skills/`

## coji — natural-japanese

- 出典: https://github.com/coji/natural-japanese （commit 9a78a42964096da509b8f3e011f0085a5f080151、2026-09-05 取得）
- 利用条件: MIT License
- こちらでの扱い: `sets/engineering/tech-writing-ja/references/japanese/` に `readability-principles.md`、`forbidden-patterns.md`、`translationese.md` を原文のまま同梱。`writing-constitution.md` は当初同梱したが、内容が pstack の technical-writing と重なるため外した
- 原本: `vendor/coji__natural-japanese/`

## Nanako0129 — sepia

- 出典: https://github.com/Nanako0129/sepia （commit 55ba9cfe57e2a23489499a26050c9c90c9843c8f、2026-09-05 取得）
- 利用条件: MIT License
- こちらでの扱い: `sets/fiction/sepia` は `skills/sepia` を一文字も変えずに置いたもの。`sets/fiction/story-architect` は sepia の fiction workflow A を途中で止めるための薄いスキルで、知識はすべて `../sepia/references/` を指す
- 原本: `vendor/Nanako0129__sepia/`
- sepia が根拠にしている研究: Russell, Rajendhran, Pham, Iyyer, Wieting (2026). *StoryScope: Investigating idiosyncrasies in AI fiction*. arXiv:2604.03136

## 鳴島悠希 — novel-Standard（長編小説執筆リポジトリ）

- 出典: 【26年8月版】ClaudeCode＆CodexCLI用の小説執筆リポジトリ配布【Opus5&5.6sol】 https://note.com/x2775co/n/n63437e236269 （MANIFEST: 2026-08-06、生成元コミット 96e95fe、2026-09-05 取得）
- 利用条件: 記事本文とパッケージに明示の記載はない。2026-09-05 に作者へ確認し、**クレジットを記載すれば public リポジトリへの同梱可**との回答を得た。参考として、同シリーズの 2026-06-10 版は「利用・改変は自由ですが改変無しの再配布は御遠慮頂けると嬉しいです」、2026-03-11 版は「改変含めご自由に。無料であれば二次配布可」と記している
- こちらでの扱い: `templates/novel/` に Claude Code 版を原文のまま置き、Codex CLI 版から `.agents/`、`.codex/`、`AGENTS.md` を加えた。ファイルの中身は変えていない。`templates/novel.json` は出典と初期化手順を持つ
- 関連記事:
  - AI小説の過剰＆均一比喩の原因は"身体部位へ情報を背負わせる圧縮癖" https://note.com/x2775co/n/n9c67657f6cd6
  - ClaudeCodeに勝てる？CodexCLI(GPT5.4）で小説執筆環境を作ってみた。 https://note.com/x2775co/n/n094f7c26ca64 （SPECIFICATION.md / MANUAL.md の配布元。参照のみ、同梱していない）

## 考え方を参考にしたもの（本文は取り込んでいない）

- Thariq (Anthropic), *The new rules of context engineering for Claude 5 generation models* https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
- 葦沢かもめ, Claude Codeで小説を書く方法 https://note.com/ashizawakamome/n/na64c50585604
- nwiizo/suiko（日本語文書の診断 CLI）https://github.com/nwiizo/suiko — 入っていれば使う旨を tech-writing-ja に書いているが、同梱していない
