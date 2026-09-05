# 長編小説執筆リポジトリ

三人称多元視点の日本語長編Web小説を、設定・時系列・人物像・伏線・情報格差を破綻させずに執筆するための Claude Code 用リポジトリ。1リポジトリ＝1作品で使う。

**Claude Code は `CLAUDE.md` と `MANUAL.md` を読めば運用方法を把握する。** 利用者向けの最短手順だけをここに置く。詳細はすべて `MANUAL.md` にある。

## 1. 必要な環境

| 必要なもの | 用途 |
|---|---|
| Claude Code | 執筆・診断・スキル実行 |
| bash | `scripts/*.sh` |
| Python 3.11以降 | `scripts/*.py` |
| GNU grep | `scripts/check.sh` のPCRE検査 |

```bash
bash --version
echo "あ" | grep -P 'あ'
```

macOS標準の grep は `-P` に非対応。GNU grep を導入するか WSL／Linux で検査する。

## 2. セットアップ

```bash
chmod +x scripts/*.sh
bash scripts/init-work.sh
python3 scripts/audit-repo.py
```

`FAIL 0` で導入完了。`init-work.sh` は既存ファイルを上書きしないので、再実行しても安全。

## 3. 使い方

このディレクトリで Claude Code を起動し、次のように依頼する。

| やりたいこと | 依頼例 |
|---|---|
| 作品設計を始める | `世界観とプロットを設計したい` |
| 企画を相談する | `/plot-advisor この異世界転生の序盤3話を詰めたい` |
| 世界観を相談する | `/worldbuilding-advisor 大陸間交易の通貨を設計したい` |
| 新しい話を書く | `/write-episode 12` または `第12話を書いて` |
| 連続して書く | `/write-episode 12-15` |
| 既存本文を検査する | `/validate-episode 12` |

執筆前に `world-bible/`、`work/character-sheet-*.md`、`work/pov-plan.md`、`work/plot.md` を埋めて凍結する。第3話まで書けたら `work/style-samples.md` を実際の本文から埋めて文体を凍結する。この順序と理由は `MANUAL.md` の第4節にある。

## 4. 本文の検査

```bash
bash scripts/check.sh --strict work/drafts/episode012.txt
python3 scripts/normalize_blanklines.py --check work/drafts/episode012.txt
bash scripts/chars.sh work/drafts/episode012.txt
python3 scripts/state_check.py --strict
```

`check.sh` は本文を、`state_check.py` は台帳（本文ファイルと状態差分ファイルの対応、作中日時と日付の正本の突合、伏線、情報格差）を検査する。本文の意味に踏み込む照合はスクリプトではなくスキルの目視手順が受け持つ。`[NG]` は必ず直す規約違反、`[警告]` は文脈で判断する統計指標。この違いは `MANUAL.md` の第8節を参照する。

## 5. ファイルの役割

| 場所 | 内容 |
|---|---|
| `CLAUDE.md` | 最優先の永続規約 |
| `MANUAL.md` | 運用マニュアル（本パッケージの取扱説明） |
| `MANIFEST.txt` | このパッケージの版情報 |
| `guidelines/` | 正書法・視点・構造・改稿の詳細規約 |
| `templates/` | 作品設計と状態管理の雛形 |
| `.claude/skills/` | 執筆・診断・相談ワークフロー |
| `work/` | 作品データ（プロット、視点表、キャラ、本文、状態台帳） |
| `world-bible/` | 世界観正典・時系列・確定事項 |
