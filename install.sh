#!/bin/sh
# agent-skills ブートストラップ。依存ゼロ (sh + git のみ)。
#
#   curl -fsSL https://raw.githubusercontent.com/chitsii/agent-skills/main/install.sh | sh
#   curl -fsSL .../install.sh | sh -s -- --global engineering   # セットまで一気に
#   ./install.sh                                                # クローン内から (そこを正にする)
set -eu

REPO_URL="${SKILLS_REPO_URL:-https://github.com/chitsii/agent-skills.git}"
BIN_DIR="$HOME/.local/bin"

# SKILLS_HOME の決定: 環境変数 > カレントがクローン > 既定
if [ -n "${SKILLS_HOME:-}" ]; then
  :
elif [ -d ./.git ] && [ -f ./bin/skills ]; then
  SKILLS_HOME="$(pwd)"
else
  SKILLS_HOME="$HOME/.local/share/agent-skills"
fi

if [ -d "$SKILLS_HOME/.git" ]; then
  # upstream があるときだけ更新。失敗しても symlink は張る。
  if git -C "$SKILLS_HOME" rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
    echo "update: $SKILLS_HOME"
    git -C "$SKILLS_HOME" pull --ff-only || echo "note: pull failed; continuing"
  else
    echo "use: $SKILLS_HOME (no upstream, skip pull)"
  fi
else
  echo "clone: $REPO_URL -> $SKILLS_HOME"
  git clone --depth 1 "$REPO_URL" "$SKILLS_HOME"
fi

mkdir -p "$BIN_DIR"
ln -sfn "$SKILLS_HOME/bin/skills" "$BIN_DIR/skills"
chmod +x "$SKILLS_HOME/bin/skills"
echo "installed: $BIN_DIR/skills -> $SKILLS_HOME/bin/skills"

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "note: $BIN_DIR が PATH にありません。fish なら:  fish_add_path $BIN_DIR" ;;
esac

if [ $# -gt 0 ]; then
  "$BIN_DIR/skills" use "$@"
fi
echo "done. 'skills list' で利用可能なセットを確認できます。"
