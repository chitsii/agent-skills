# agent-skills

Claude Code と Codex CLI で共用する、自分用の Agent Skills。
このリポジトリを唯一の正として、`skills` コマンドが両ツールの探索パスへスキルを配置する。

**方針**

- スキルには「ルール」ではなく「判断基準」を書く。モデルが知っていること・コードを見れば分かることは書かない
- 入れるのは必要最小限。用途別のセット（`engineering` / `fiction`）に分け、作業中のリポジトリに必要なものだけ張る
- 他者のスキルは `vendor/` に原本を置いて読むだけ。有効化するのは自分の言葉で書き直した `sets/` のものだけ

## インストール

```bash
curl -fsSL https://raw.githubusercontent.com/chitsii/agent-skills/main/install.sh | sh
```

セットまで一気に入れる場合:

```bash
curl -fsSL https://raw.githubusercontent.com/chitsii/agent-skills/main/install.sh | sh -s -- --global engineering
```

やること: `~/.local/share/agent-skills` にクローン → `~/.local/bin/skills` に symlink → （引数があれば）`skills use`。
依存は `sh` と `git` と `python3` だけ。`~/.local/bin` が PATH にない場合は最後に案内が出る。

開発機（このリポジトリを直接編集する端末）では、クローンの中で実行するとそこが正になる:

```bash
git clone https://github.com/chitsii/agent-skills.git ~/programming/projects/skills
cd ~/programming/projects/skills && ./install.sh
```

## 使い方

```bash
cd ~/projects/my-rust-cli
skills use engineering          # このリポジトリに engineering セットを配置する

cd ~/projects/my-novel
skills use fiction              # こちらには fiction

skills status                   # ここと global に何が配置されているか (古いコピーは STALE)
skills list                     # 利用可能なセットとスキル（description つき）
skills doctor                   # 両ツールが実際に認識しているか検証
skills sync                     # git pull → 壊れたものを掃除 → 配置済みセットを更新
skills drop fiction             # 外す
skills use engineering --global # 全プロジェクト共通で常設したいとき
```

`skills use` はリポジトリのどのサブディレクトリから実行しても git toplevel に配置する。
git 管理外のディレクトリではカレントディレクトリに配置する。

既定は**コピー**。プロジェクト内に実体があるので、グローバル設定を一切触らずにどの環境でも動く。
`--link` を付けると symlink になり編集が即反映されるが、Claude Code がスキルの `references/` を読むには
`~/.claude/settings.json` の `permissions.additionalDirectories` にこのリポジトリを足す必要がある（下記「仕組み」）。

### 日々の運用

| 状況 | やること |
|---|---|
| 新しいリポジトリで作業を始める | `skills use <set>` |
| スキルを追加・変更・削除した | 配置しているリポジトリで `skills sync`（`skills status` が STALE を教えてくれる） |
| 別の端末で最新にしたい | `skills sync`（`git pull` を含む） |
| 発火しない | `skills doctor` → Codex の認識を確認。Claude Code はセッション内で `/skills` か `/skill-doctor` |

## 仕組み

```
~/.local/bin/skills  ─symlink→  <repo>/bin/skills          ← 自分の realpath から repo を特定
<project>/.claude/skills/<name>/   ← <repo>/sets/<set>/<name>/ のコピー   (Claude Code)
<project>/.agents/skills/<name>/   ← 同上                                 (Codex CLI)
```

- 探索パスは実測で確定したもの（[docs/research.md §2](docs/research.md)）。**`~/.codex/skills` は使わない**。Codex が起動時に `.system/` を書き込む場所
- コピーした各スキル dir に `.agent-skills.json`（由来のセットと内容ハッシュ）を置く。`status` / `sync` はこれで自分が配置したものを見分け、元と違えば STALE と報告する
- project スコープでは配置したスキル名を `.git/info/exclude` に書く。共有の `.gitignore` は触らない
- symlink を既定にしない理由: Claude Code は `Read` 時に symlink を実体に解決し、プロジェクト外なら権限で弾く。SKILL.md 本体はハーネスが読むので動くが、`references/` が読めない。回避には `additionalDirectories` へのグローバル設定変更が要り、それを前提にしたくない

## リポジトリ構成

```
agent-skills/
├── install.sh              ブートストラップ（POSIX sh、依存ゼロ）
├── bin/skills              本体（Python 3）
├── sets/
│   ├── engineering/        ソフトウェア設計・実装・技術文書
│   │   └── <name>/SKILL.md
│   └── fiction/            小説・シナリオ
│       └── <name>/SKILL.md
├── vendor/                 参考にした他者のスキルの原本（有効化しない）
│   ├── README.md
│   └── VENDOR.tsv          出典台帳
└── docs/research.md        探索パス・symlink・frontmatter 互換の調査記録
```

`sets/<set>/` 直下の、`SKILL.md` を持つディレクトリだけがスキルとして扱われる。

## スキルを追加する

1. `sets/<set>/<name>/SKILL.md` を作る。ディレクトリ名 = スキル名（小文字とハイフン）
2. frontmatter は **Agent Skills 仕様の 6 フィールドだけ**を使う。両ツールで確実に通り、claude.ai や Skills API へ上げるときもエラーにならない

   ```yaml
   ---
   name: design-doc
   description: 基本設計書を書くとき、設計レビューの前に使う。呼び出し側→型の骨組み→候補比較→rationale の順で書く。
   license: MIT                       # 任意
   metadata:                          # 任意。自由形式
     derived_from: https://github.com/...
   ---
   ```

   使えるのは `name` / `description` / `license` / `compatibility` / `metadata` / `allowed-tools`。
   Claude Code 固有のキー（`disable-model-invocation`, `context`, `paths` など）は Codex では無視される。使うならそのスキルは Claude Code 専用と割り切る

3. **`description` に発火条件を書く。** 両ツールとも起動時に読むのは `name` と `description` だけで、本文は呼ばれるまで読まれない。「〜するとき」「〜した直後」の形で具体的に。曖昧な description のスキルは存在しないのと同じ
4. 本文は短く、詳細は `references/` に置いて必要時だけ読ませる。本文の長さはコンテキストを常時圧迫しない（一覧に載るのは description だけ）
5. 張っているリポジトリで `skills sync`

### スキルにしないもの

「常に効かせたいこと」はスキルではなく `CLAUDE.md` / `AGENTS.md` に書く。スキルは条件付きで読み込まれるので、常時性のあるものを入れると発火漏れする。
「確実に守らせたいこと」は文章ではなく hooks やスクリプトにする。

## 他者のスキルを取り込む

nvim の設定と同じ扱い。他人のものはベースにして、自分のものを書く。

1. 作者が明確なリポジトリからだけ取る（集約サイト・まとめ記事からは入れない）
2. 読んでから、`vendor/<owner>__<repo>/<元のパス>/` に取得時点の内容をそのままコピー
3. `vendor/VENDOR.tsv` に 1 行追加（source, path, commit, date, license）
4. `sets/` に自分の言葉で書き直す。frontmatter の `metadata.derived_from` に出典 URL（commit 固定）、`license` に元のライセンス
5. 上流は追わない。必要になったら取り直して diff を読む

## 検証

```bash
skills doctor            # リンク健全性 + Codex が実際にスキャンしたルートと認識スキル名（API 呼び出しなし）
skills doctor --claude   # 加えて Claude Code (haiku) に 1 回問い合わせて認識を確認
```

Claude Code のセッション内では `/skill-doctor` で各スキルのコンテキスト負担と使用頻度を見られる。

## 既知の制約

- Claude Code はスキル一覧にコンテキスト窓の 1% を割り当て、超えると使用頻度の低いスキルから description を落とす（設定 `skillListingBudgetFraction`）。セットを分けているのはこのためというより、無関係なスキルの誤発火を防ぐため
- Codex にはスキル単位の無効化設定がない。両ツール共通で効くのは物理配置だけ
- `skills sync` の更新は global とカレントのプロジェクトだけが対象。他のプロジェクトはそこで `skills sync` を実行する
- コピーした側を直接編集しない。次の `sync` で上書きされる。直すのは `sets/`

## ライセンス

MIT。`vendor/` 内の各原本はそれぞれのライセンスに従う。
