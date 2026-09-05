# vendor/ — 参考にした他者のスキル（原本・読むだけ）

ここにあるものは **有効化しない**。`sets/` に自分の言葉で書き直したものだけを張る。
nvim の設定で他人の dotfiles を参考にするのと同じ扱い。

- 置き方: `vendor/<owner>__<repo>/<元のパス>/` に、取得時点の内容をそのままコピー
- 記録: `vendor/VENDOR.tsv` に 1 行（source, path, commit, date, license）
- 更新: 追わない。必要になったら新しい commit を取り直して diff を読む
- 書き直した側 (`sets/**/SKILL.md`) の frontmatter に出典を残す:

```yaml
license: MIT
metadata:
  derived_from: https://github.com/mattpocock/skills/tree/<commit>/skills/productivity/grilling
```

取り込み元は作者が明確なリポジトリのみ（集約サイト・まとめ記事からは入れない）。
