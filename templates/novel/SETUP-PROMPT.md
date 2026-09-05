# セットアップ指示 — 受け取り側のClaude Codeへ貼り付ける

`novel-Standard-template.zip` と本ファイルを同じディレクトリに置き、そのディレクトリで Claude Code を開始する。下の枠内をそのまま貼り付ければ、環境確認、展開、初期化、動作検証までが一度に進む。

---

==== ここからコピー ====

`novel-Standard-template.zip` は、日本語長編Web小説を執筆するための Claude Code 用リポジトリです。次を順に実行し、既存ファイルを上書きせずにセットアップしてください。セットアップ中に小説本文は書かないでください。

1. 環境を確認する。`bash --version`、`python3 --version`（3.11以降）、`echo "あ" | grep -P "あ"`（`あ` が出力されること。出力されない場合はGNU grepではないので、検査スクリプトが動かない）。不足があれば何も変更せず報告する。
2. zipを展開する。`unzip` がなければ `python3 -m zipfile -e novel-Standard-template.zip .` を使う。
3. 展開された `novel-Standard/` に入り、`chmod +x scripts/*.sh` を実行する。
4. `MANUAL.md` を読む。これが本リポジトリの取り扱いマニュアルで、運用手順、正本の一覧、完了条件、禁止事項が書かれている。以後は `CLAUDE.md` と `MANUAL.md` に従って作業する。
5. `bash scripts/init-work.sh` を実行して `work/` と `world-bible/` を生成する。既存ファイルは上書きしないので、再実行しても安全である。
6. `python3 scripts/audit-repo.py` を実行し、`FAIL 0` を確認する。FAILが1件でもあれば内容を報告し、解消するまで執筆へ進まない。
7. 次のスモークテストを行う。

   ```bash
   printf 'これは確認用の文章。\n彼は静かに言った。\n' > /tmp/_smoke.txt
   bash scripts/check.sh --strict /tmp/_smoke.txt
   python3 scripts/normalize_blanklines.py --check /tmp/_smoke.txt
   rm -f /tmp/_smoke.txt
   python3 scripts/state_check.py
   ```

   `check.sh` が「違反なし」、`normalize_blanklines.py` が `OK`、`state_check.py` が `NG 0` で終わることを確認する。初期化直後は本文も状態差分もないため、`state_check.py` は検査省略の情報行だけを出す。これは正常である。

8. `.claude/skills/` 直下のスキル名を一覧表示し、`MANUAL.md` にもとづいて「執筆を始めるには何を用意すればよいか」を3〜5行で説明して終了する。

破壊的操作、外部インストール、既存ファイルの置換が必要になった場合だけ確認してください。

==== ここまで ====

---

セットアップ後の進め方は `MANUAL.md` を正本とする。世界観、キャラクターシート、視点計画、プロットを `MANUAL.md` の「執筆を始める前に凍結する設計」に従って作り、`/write-episode 1`（または「第1話を書いて」）で執筆へ入る。

受け取ったパッケージの版は `MANIFEST.txt` で確認できる。
