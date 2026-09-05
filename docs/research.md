# 調査記録 — Claude Code × Codex CLI のスキル共有

> これは設計判断の根拠を残した調査記録。**現在の使い方は [../README.md](../README.md)**。
> ここでの結論は `install.sh` と `bin/skills` として実装済み。

調査日: 2026-09-05
検証環境: macOS 15.7.3 (arm64) / Claude Code **2.1.261** / codex-cli **0.153.4** (Homebrew Cask)

このリポジトリを「スキルの唯一の正」にして、Claude Code と Codex CLI の両方から
symlink で参照させる、というのが結論。以下はその根拠と手順。

> このドキュメントの記述のうち「実測」と書いてある部分は、上記バージョンで実際に
> プローブ用スキルを配置して挙動を確認した結果。ネット上の記事は古いバージョンの
> 情報が多く、現行挙動とズレていたので実測を優先している。

---

## 0. 結論（実装済み）

このリポジトリを唯一の正とし、`bin/skills` がスキル単位の symlink を
`~/.claude/skills` / `~/.agents/skills`（global）または各プロジェクトの
`.claude/skills` / `.agents/skills`（project）へ張る。根拠は以下の各節。

---

## 1. 調査時点の棚卸し（両方まっさら）

`SKILL.md` をホーム配下で全探索して **0件**。つまりゼロから設計できる状態だった。

### Claude Code

| 項目 | 状態 |
|---|---|
| `~/.claude/skills/` | 空（調査中に作成された） |
| プロジェクト `.claude/skills/` | なし。`.claude` は3プロジェクトにあるが中身は `settings.local.json` のみ |
| インストール済みプラグイン | **ゼロ**（`plugins/config.json` は `{"repositories": {}}`） |
| マーケットプレイス | `claude-plugins-official` を登録・キャッシュ済みだが未インストール（公式39 + 外部15が選べる） |
| MCP | `gemini-cli` のみ |
| `~/.claude/settings.json` | 3行のみ（fullscreen TUI / 危険モード確認スキップ / 通知） |

### Codex CLI

| 項目 | 状態 |
|---|---|
| `~/.codex/` | 調査開始時は実質空（`config.toml` すらない＝初回起動前） |
| スキル機能 | **対応済み**。feature flag `skill_search` と `skill_mcp_dependency_install` が `stable / true` |
| プラグイン | `No marketplace plugins found.` |
| ログイン | **未ログイン**（`codex login status` → `Not logged in`）。使い始めるには `codex login` が必要 |

### dotfiles

**chezmoi** で管理中（source: `~/.local/share/chezmoi`、git 管理下）。
ただし現在の管理対象は `private_dot_config` のみで、**`.claude` も `.codex` も chezmoi 管理外**。

> 調査の副作用: `codex doctor` / `codex debug` を実行したため `~/.codex/` が初期化された
> （`installation_id`、`shell_snapshots`、`skills/.system/` 等）。`config.toml` は未作成のまま。

---

## 2. 探索パス（実測で確定）

`codex debug prompt-input` は、モデルに渡る developer メッセージを JSON でそのまま
ダンプしてくれる。ここに `### Skill roots` テーブルが含まれるので、
**推測ではなく実際のスキャン対象を直接確認できる**（APIコール不要・未ログインでも動く）。

プローブスキルを4箇所に置いて実行した結果、Codex は以下 **5系統** をスキャンしていた:

| ツール | ユーザースコープ | プロジェクトスコープ | その他 |
|---|---|---|---|
| **Codex** | `~/.agents/skills`<br>`~/.codex/skills` | `.agents/skills`<br>`.codex/skills` | `~/.codex/skills/.system`（自動生成）<br>`/etc/codex/skills` |
| **Claude Code** | `~/.claude/skills` | `.claude/skills`（起動ディレクトリから repo root まで遡る） | プラグイン、エンタープライズ |

ディレクトリ構造は両者とも `<skills-root>/<skill-name>/SKILL.md` で**完全に同一**。

> 📌 公式ドキュメントは `.agents/skills` 系しか記載していないが、`.codex/skills` 系も
> 現役で動く。ただし移植性の観点では `.agents` 側が正式。

### ⚠️ 落とし穴: `~/.codex/skills` を symlink にしてはいけない

Codex は起動時に **`~/.codex/skills/.system/` へ自前のシステムスキルを書き込む**。
実測で以下が自動生成された:

```
~/.codex/skills/.system/
├── .codex-system-skills.marker
├── imagegen/
├── openai-docs/
├── plugin-creator/
├── review-agent/
├── skill-creator/
└── skill-installer/
```

したがって `~/.codex/skills` 自体を git リポジトリへの symlink にすると、
**リポジトリが Codex の生成物で汚染される**。

→ **Codex 側の共有ルートには `~/.agents/skills` を使う。**

---

## 3. symlink 対応状況（実測）

| ケース | Codex | Claude Code 2.1.261 |
|---|---|---|
| **スキル単位** symlink（`~/.X/skills/foo` → 外部ディレクトリ） | ✅ 追従 | ✅ 追従（実測確認） |
| **ルートごと** symlink（`~/.X/skills` 自体が symlink） | ✅ 追従 | ✅ 追従（実測確認） |

### ネット情報との食い違いについて

「Claude Code は symlink されたスキルを見つけられない」という記事・Issue が多数あるが、
これは **v2.1.69 〜 v2.1.81 頃のリグレッション**であり、**2.1.261 では両方とも直っている**。

- [#38051](https://github.com/anthropics/claude-code/issues/38051) — `~/.claude/skills` がsymlinkだとユーザースキルが読まれない（v2.1.69 の symlink セキュリティ修正が原因、Closed）
- [#14836](https://github.com/anthropics/claude-code/issues/14836) — `/skills` が symlink 先を辿らない（v2.0.73、Open のまま）

実測方法: `~/.claude/skills/` に実体スキルと symlink スキルを1つずつ置き、
`claude --model haiku -p "..."` で列挙させたところ**両方見えた**。
`~/.claude/skills` 自体を symlink に差し替えた場合も認識された。
現行の[公式ドキュメント](https://code.claude.com/docs/en/skills)にも symlink 追従が明記されている。

**それでも「スキル単位リンク」を採用する理由**: 壊れた前科があるのはルートごと
symlink のほう。将来のリグレッションに対して脆いのが分かっているので、
そちらは避けておく。加えてスキル単位なら、共有スキルとツール固有スキルを
同じルートに共存させられる。

---

## 4. frontmatter の互換性（実測）

### 結論: Codex のローダーは未知のキーを黙って無視する

以下を全部盛りにした `SKILL.md` を `~/.agents/skills` に置いて Codex に読ませたところ、
**エラーも警告もなくロードされた**:

```yaml
---
name: probe-cckeys
description: ...
allowed-tools: Read Grep      # Claude 固有
model: inherit                # Claude 固有
context: fork                 # Claude 固有
paths: "**/*.py"              # Claude 固有
metadata:                     # 仕様フィールド
  owner: me
license: MIT                  # 仕様フィールド
---
```

`disable-model-invocation: true` を付けたスキルも問題なくロードされた。

> Codex バイナリ内に `Unexpected key(s) in SKILL.md frontmatter` という厳格な
> バリデータ文字列があるが、これは `skill-creator` / `skill-installer` スキルに
> 同梱された Python スクリプトのものであって、ランタイムの読み込み経路ではない。

### それでも共有スキルは「仕様6フィールド」に留める

実用上は動くが、移植性のために共有スキルは Agent Skills 仕様のフィールドだけに絞る:

```yaml
---
name: my-skill
description: 何をするスキルで、どういうときに使うか。自動起動の判断材料になるので具体的に。
---
```

仕様として両対応が保証されるのは **`name` / `description` / `license` / `compatibility` /
`metadata` / `allowed-tools`** の6つ。必須は `name` と `description` のみ。

理由は Codex 対策だけではない。**claude.ai や Skills API へアップロードする際、
それ以外の Claude Code 固有キー（`disable-model-invocation`, `context`, `paths`, `shell` 等）は
ハードエラーになる**。将来スキルを配布する可能性を残すなら6フィールドに揃えておく。

### ツール固有の拡張はどこに置くか

| | 置き場所 | 相手ツールから見ると |
|---|---|---|
| Codex 固有（UIメタデータ、MCP依存） | スキル内の `agents/openai.yaml` | ただの未知のサブディレクトリ。無視される |
| Claude Code 固有（`context: fork` 等） | frontmatter | 無視される（実測） |

どちらも衝突しない。ただし Claude 固有キーを多用するスキルは、共有せず
`~/.claude/skills` に実体で置くほうが素直。

---

## 5. 採用する共有方法

### 構成

```
~/programming/projects/skills/          ← git repo（唯一の正）
├── README.md
├── bin/skills                           ← use / drop / status / sync / doctor
└── <skill-name>/
    └── SKILL.md                         ← 仕様6フィールドのみ

~/.claude/skills/<skill-name>  ─symlink→  ~/programming/projects/skills/<skill-name>
~/.agents/skills/<skill-name>  ─symlink→  ~/programming/projects/skills/<skill-name>
```

### 採用理由

- `~/.codex/skills` を避けることで `.system` 汚染を回避（§2）
- スキル単位リンクなので、過去にリグレッションした経路を踏まない（§3）
- 各ツール固有のスキルは、各ルートに実体で置いて共存できる
- `bin/link.sh` は冪等な数行で済み、外部ツール依存が要らない
- 既存の chezmoi 運用と競合しない（後から `run_onchange_` スクリプトとして載せることも可能）

### 初期案 bin/link.sh（現在は `bin/skills` に置き換え済み。記録として残す）

```bash
#!/usr/bin/env bash
# 共有スキルを Claude Code と Codex CLI の両方へ symlink する。冪等。
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills")

for t in "${TARGETS[@]}"; do
  mkdir -p "$t"
  # 1. このリポジトリを指す壊れた/古いリンクを掃除
  for link in "$t"/*; do
    [ -L "$link" ] || continue
    case "$(readlink "$link")" in
      "$SRC"/*) [ -e "$link" ] || rm "$link" ;;
    esac
  done
  # 2. SKILL.md を持つディレクトリだけリンク
  for skill in "$SRC"/*/; do
    name="$(basename "$skill")"
    [ -f "$skill/SKILL.md" ] || continue
    ln -sfn "${skill%/}" "$t/$name"
    echo "linked: $t/$name"
  done
done
```

```bash
chmod +x bin/link.sh && ./bin/link.sh
```

`bin/` は `SKILL.md` を持たないので自動的にスキップされる。

---

## 6. 検討したが採用しなかった選択肢

| 方式 | 内容 | 見送り理由 |
|---|---|---|
| [skillshare](https://github.com/runkids/skillshare) | 単一 Go バイナリ。`~/.config/skillshare/skills` を正として60+ツールへ symlink 配布。copy モード、`skillshare audit`（prompt injection スキャン）、Gemini TOML 等への形式変換あり | 2ツールだけなら過剰。**3つ目以降のツールを足すときに再検討する価値あり**（特に audit 機能） |
| [sync-claude-skills-to-codex](https://github.com/ariccb/sync-claude-skills-to-codex) | Claude → Codex 一方向。`~/.claude/skills` と `~/.claude/plugins/cache` から `~/.codex/skills` へ symlink | 一方向で Claude 側が正になる。`~/.codex/skills` を使うので §2 の問題を踏む。プラグイン更新でリンクが切れる既知の弱点あり |
| chezmoi で管理 | 既存 dotfiles 運用に統合。`chezmoi apply` で配布 | スキルは実体ファイルが増えていく性質なので、独立した git repo のほうが扱いやすい。**他マシンへ展開する必要が出たら、この repo を chezmoi から clone する形で後付けできる** |
| SessionStart フック | セッション開始時にリンクを張り直す | 手動リンクが腐り始めたら補強策として追加する |

---

## 7. 初期スキルの調達先

自分で書くのが基本だが、参考にできるものが手元・近くにある。

- **Codex 同梱のシステムスキル**: `~/.codex/skills/.system/` に実物がある。
  特に `skill-creator` と `skill-installer` は書き方の参考になる
- **Claude 公式マーケットプレイス**: キャッシュ済み。
  `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/` に
  `skill-creator` / `code-review` / `feature-dev` など39個。まだ未インストール
- **openai/skills**: Codex の参照実装リポジトリ
  （`skills/.curated` / `.experimental` / `.system`）

---

## 参考リンク

- [Build skills — OpenAI Codex 公式](https://learn.chatgpt.com/docs/build-skills)
- [Agent Skills — Claude Code 公式](https://code.claude.com/docs/en/skills)
- [Agent Skills spec](https://agentskills.io)
- [Codex vs Claude Code Skills: Setup, Settings, and How to Share Skills Across Both — Kanaries](https://docs.kanaries.net/articles/codex-vs-claude-code-skills)
- [runkids/skillshare](https://github.com/runkids/skillshare)
- [ariccb/sync-claude-skills-to-codex](https://github.com/ariccb/sync-claude-skills-to-codex)
- [claude-code #38051](https://github.com/anthropics/claude-code/issues/38051) / [#14836](https://github.com/anthropics/claude-code/issues/14836)
