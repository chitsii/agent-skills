#!/usr/bin/env python3
"""novel-Standard の構成・Skill・スクリプトをまとめて監査する。"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"
REQUIRED_PATHS = (
    "CLAUDE.md",
    ".gitattributes",
    ".claude/settings.json",
    "guidelines/00-overview.md",
    "guidelines/01-writing-rules.md",
    "guidelines/02-narrative-craft.md",
    "guidelines/03-character-and-world.md",
    "guidelines/04-structure-and-plot.md",
    "guidelines/05-ai-guardrails.md",
    "guidelines/06-revision-checklist.md",
    "templates/plot.md",
    "templates/pov-plan.md",
    "templates/scene-card.md",
    "templates/current-state.md",
    "templates/episode-state-delta.md",
    "templates/world-bible-index.md",
    "templates/timeline.md",
    "templates/canon-log.md",
    "templates/style-samples.md",
    "templates/phrase-allowlist.txt",
    "templates/vocab-watchlist.tsv",
    "templates/cliche-allowlist.txt",
    "templates/sweep-adjudicated.tsv",
    "templates/motif-dictionary.tsv",
    "templates/pending-decisions.md",
    "scripts/check.sh",
    "scripts/repeat_check.py",
    "scripts/vocab_check.py",
    "scripts/cliche_check.py",
    "scripts/init-work.sh",
    "scripts/normalize_blanklines.py",
    "scripts/state_check.py",
)

# SKILL.md の本体行数の上限。これを超えると読み込み時に他の文脈を圧迫するため、
# 参照ファイルへ分割する（Anthropicのスキル作成ガイドラインの推奨値）。
SKILL_BODY_MAX_LINES = 500

# 参照ファイルが長くなりすぎたときに分割を促す目安。
REFERENCE_WARN_LINES = 500


def find_bash() -> str | None:
    """PATHまたはGit for Windowsの標準配置からbashを探す。"""
    candidates: list[Path] = []
    if os.name == "nt":
        git = shutil.which("git")
        if git:
            candidates.append(Path(git).resolve().parent.parent / "bin" / "bash.exe")
        for variable in ("ProgramFiles", "ProgramFiles(x86)"):
            program_files = os.environ.get(variable)
            if program_files:
                candidates.append(Path(program_files) / "Git" / "bin" / "bash.exe")

    bash = shutil.which("bash")
    if bash:
        candidates.append(Path(bash))

    return next((str(path) for path in candidates if path.is_file()), None)


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class Audit:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.passes = 0

    def ok(self, message: str) -> None:
        self.passes += 1
        print(f"PASS  {message}")

    def fail(self, message: str) -> None:
        self.failures.append(message)
        print(f"FAIL  {message}")

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        print(f"WARN  {message}")

    def check(self, condition: bool, success: str, failure: str) -> None:
        self.ok(success) if condition else self.fail(failure)


def run(command: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def parse_frontmatter(path: Path) -> tuple[dict[str, str], set[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, set()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, set()
    data: dict[str, str] = {}
    keys: set[str] = set()
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            key, value = match.groups()
            keys.add(key)
            data[key] = value.strip().strip('"\'')
    return data, keys


def audit_layout(audit: Audit) -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    audit.check(not missing, "必須ファイルが揃っている", f"必須ファイルが不足: {', '.join(missing)}")

    try:
        settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        audit.fail(f".claude/settings.json を解析できない: {exc}")
        return
    permissions = settings.get("permissions", {})
    valid = isinstance(settings, dict) and isinstance(permissions.get("allow", []), list)
    audit.check(
        valid,
        "Claude Code設定（.claude/settings.json）が有効なJSONで permissions を持つ",
        "Claude Code設定が不正（permissions.allow のリストを確認）",
    )


def audit_skills(audit: Audit) -> None:
    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    bad: list[str] = []
    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            bad.append(f"{skill_dir.name}: SKILL.mdなし")
            continue
        metadata, keys = parse_frontmatter(skill_file)
        if keys != {"name", "description"}:
            bad.append(f"{skill_dir.name}: frontmatter keys={sorted(keys)}")
        if metadata.get("name") != skill_dir.name:
            bad.append(f"{skill_dir.name}: name={metadata.get('name')!r}")
        description = metadata.get("description", "")
        if not description or len(description) > 1024:
            bad.append(f"{skill_dir.name}: description長={len(description)}")

    audit.check(
        not bad,
        f"{len(skill_dirs)}個のSkill構造・frontmatterが整合",
        "Skill監査: " + " / ".join(bad),
    )


def audit_skill_budget(audit: Audit) -> None:
    """SKILL.mdの分量と、参照の入れ子を検査する。

    SKILL.mdが長いと読み込み時に他の文脈を圧迫する。参照が2階層以上に
    なると、Claudeが途中までしか読まずに情報を取りこぼすことがある。
    """
    too_long: list[str] = []
    nested: list[str] = []
    long_references: list[str] = []

    for skill_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        skill_text = skill_file.read_text(encoding="utf-8")
        lines = skill_text.splitlines()
        if len(lines) > SKILL_BODY_MAX_LINES:
            too_long.append(f"{skill_dir.name}: {len(lines)}行")

        # SKILL.md から直接たどれる参照は1階層目とみなす。
        direct = {
            Path(target.strip().strip("<>").split("#", 1)[0]).name
            for target in LINK_RE.findall(skill_text)
        }

        for reference in sorted((skill_dir / "references").glob("*.md")):
            text = reference.read_text(encoding="utf-8")
            if len(text.splitlines()) > REFERENCE_WARN_LINES:
                long_references.append(
                    f"{skill_dir.name}/{reference.name}: {len(text.splitlines())}行"
                )
            for target in LINK_RE.findall(text):
                cleaned = target.strip().strip("<>").split("#", 1)[0]
                if not cleaned or re.match(r"^(?:https?://|mailto:|#)", cleaned):
                    continue
                target_name = Path(cleaned).name
                # SKILL.md からも直接たどれるなら、実質1階層なので問題にしない。
                if target_name.endswith(".md") and target_name not in direct:
                    nested.append(f"{skill_dir.name}/{reference.name} -> {cleaned}")

    audit.check(
        not too_long,
        f"SKILL.mdはいずれも{SKILL_BODY_MAX_LINES}行以内",
        f"SKILL.mdが長すぎる（参照ファイルへ分割する）: {', '.join(too_long)}",
    )
    if nested:
        audit.warn("参照が入れ子になっている（SKILL.mdから1階層に保つ）: " + ", ".join(nested))
    if long_references:
        audit.warn("参照ファイルが長い（分割を検討）: " + ", ".join(long_references))


def audit_distribution(audit: Audit) -> None:
    """生成済みの配布zipが方針どおりかを検査する。

    配布物として展開されたコピーには dist/package が無い。その場合、
    配布物を作る側の検査は対象外なので何もしない。
    """
    if not (ROOT / "dist/package").is_dir():
        return

    archives = sorted((ROOT / "dist").glob("*.zip"))
    if not archives:
        audit.warn("配布zipが未生成（bash scripts/build-dist.sh で作成できる）")
        return

    for archive in archives:
        try:
            with zipfile.ZipFile(archive) as handle:
                names = handle.namelist()
        except (OSError, zipfile.BadZipFile) as exc:
            audit.fail(f"{archive.name} を読めない: {exc}")
            continue

        problems: list[str] = []
        if any(".pyc" in name or "__pycache__" in name for name in names):
            problems.append("Pythonバイトコードが混入している")
        if any("novel-write-r18" in name for name in names):
            problems.append("成人向けスキルが混入している")
        for required in ("MANUAL.md", "README.md", "CLAUDE.md", "scripts/state_check.py"):
            if not any(name.endswith(f"novel-Standard/{required}") for name in names):
                problems.append(f"{required} が入っていない")

        audit.check(
            not problems,
            f"{archive.name} の同梱物が配布方針どおり",
            f"{archive.name}: " + " / ".join(problems),
        )

        # 配布物に入らない場所の更新は、zipの鮮度に関係しない。
        # novel-write-r18 は配布方針上zipへ入れない（上の同梱物検査が非同梱を強制する）。
        excluded_parts = {".git", "dist", "work", "world-bible", "__pycache__", "tests", "novel-write-r18"}
        excluded_names = {"settings.local.json", "build-dist.sh", "eval.sh"}
        archive_mtime = archive.stat().st_mtime
        newer = [
            str(path.relative_to(ROOT))
            for path in ROOT.rglob("*")
            if path.is_file()
            and not any(part in excluded_parts for part in path.parts)
            and path.name not in excluded_names
            and path.stat().st_mtime > archive_mtime
        ]
        if newer:
            audit.warn(
                f"{archive.name} が最新の変更を含んでいない可能性がある"
                f"（{len(newer)}ファイルがzipより新しい。先頭: {', '.join(sorted(newer)[:3])}）"
            )


def audit_markdown_links(audit: Audit) -> None:
    broken: list[str] = []
    # 配布物では README.md が差し替わり MANUAL.md が加わる。存在するものだけ検査する。
    roots = [ROOT / name for name in ("CLAUDE.md", "README.md", "MANUAL.md")]
    for folder in (ROOT / "guidelines", ROOT / "templates", SKILLS_DIR, ROOT / ".claude/commands"):
        roots.extend(folder.rglob("*.md"))
    for source in roots:
        if not source.is_file():
            continue
        text = source.read_text(encoding="utf-8")
        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^(?:https?://|mailto:|#)", target):
                continue
            if any(mark in target for mark in ("<", ">", "*", "|")):
                continue
            resolved = (source.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{source.relative_to(ROOT)} -> {raw_target}")
    audit.check(not broken, "Markdownの相対リンクに参照切れなし", "参照切れ: " + " / ".join(broken))


def audit_source_syntax(audit: Audit) -> None:
    bad_python: list[str] = []
    for path in sorted(ROOT.rglob("*.py")):
        if any(part in {".git", "work", "dist"} for part in path.parts):
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (SyntaxError, UnicodeError) as exc:
            bad_python.append(f"{path.relative_to(ROOT)}: {exc}")
    audit.check(not bad_python, "Pythonファイルの構文検査合格", "Python構文エラー: " + " / ".join(bad_python))

    bash = find_bash()
    if not bash:
        audit.fail("bashが見つからずシェルスクリプトを検査できない")
        return
    bad_shell: list[str] = []
    shell_files = sorted((ROOT / "scripts").glob("*.sh"))
    for path in shell_files:
        result = run([bash, "-n", path.relative_to(ROOT).as_posix()])
        if result.returncode:
            bad_shell.append(f"{path.name}: {result.stdout.strip()}")
    audit.check(not bad_shell, "Bashファイルの構文検査合格", "Bash構文エラー: " + " / ".join(bad_shell))

    crlf = [str(path.relative_to(ROOT)) for path in shell_files if b"\r\n" in path.read_bytes()]
    audit.check(not crlf, "Bash実行ファイルはLF改行", "CRLF混入: " + ", ".join(crlf))


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module specを作れない: {path}")
    module = importlib.util.module_from_spec(spec)
    # dataclass などモジュール名から自分自身を引く機能があるため、
    # exec_module の前に sys.modules へ登録しておく。
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        del sys.modules[name]
        raise
    return module


def audit_python_smoke(audit: Audit) -> None:
    try:
        blanklines = load_module(ROOT / "scripts/normalize_blanklines.py", "normalize_blanklines")
        normalized = blanklines.normalize("甲\n\n乙\n")
        if normalized != "甲\n乙\n":
            raise AssertionError(f"空行正規化結果={normalized!r}")

        collapsed = blanklines.normalize("甲\n\n\n\n乙\n")
        if collapsed != "甲\n\n乙\n":
            raise AssertionError(f"空行圧縮結果={collapsed!r}")

        state = load_module(ROOT / "scripts/state_check.py", "state_check")
        if state.episode_number("第12話") != 12 or state.episode_number("ep012") != 12:
            raise AssertionError("話数の解釈に失敗")
        # 区切り行と記入例の行は落とし、見出し行と実データは残す
        # （見出し行は呼び出し側がID書式で弾く）
        rows = state.parse_table_rows(
            "| ID | 内容 | 設置章 |\n|---|---|---|\n| F001 | （例：無視される行）| 第1話 |\n"
            "| F002 | 実データ | 第3話 |\n",
            min_columns=3,
        )
        identifiers = [row[0] for row in rows]
        if identifiers != ["ID", "F002"]:
            raise AssertionError(f"表の解析結果={identifiers!r}")
        # 08-timeline は §3 だけを見る（§2 の史実年表の年号を話数と読まない）
        section = state.timeline_section3(
            "## 2. 史実年表\n| 帝国暦398年 | 即位 |\n\n## 3. 話別作中日付\n| 第1話 | 三月二日 |\n\n## 99. 訂正ログ\n"
        )
        if "第1話" not in section or "史実年表" in section or "訂正ログ" in section:
            raise AssertionError(f"§3の切り出し結果={section!r}")
        # 「開始〜終了」の範囲表記と当該話の日時は、完全一致しなくても同じ日を指す
        if not state.dates_agree("帝国暦412年3月2日", "帝国暦412年3月2日〜3月3日"):
            raise AssertionError("範囲表記の日付照合に失敗")
        if state.dates_agree("帝国暦412年3月2日", "帝国暦412年3月5日"):
            raise AssertionError("日付の不一致を検出できていない")
    except Exception as exc:  # 監査では個別例外を集約して表示する
        audit.fail(f"Python機能スモークテスト失敗: {exc}")
    else:
        audit.ok("空行正規化・状態台帳パーサのスモークテスト合格")


def audit_executable_workflows(audit: Audit) -> None:
    bash = find_bash()
    if not bash:
        audit.fail("bashが見つからず実行ワークフローを検査できない")
        return
    with tempfile.TemporaryDirectory(prefix=".audit-", dir=ROOT) as temp_name:
        temp = Path(temp_name)
        good = temp / "good.txt"
        bad = temp / "bad.txt"
        good.write_text("彼は湯飲みを置いた。\n「もう行く」\n", encoding="utf-8")
        bad.write_text("**強調**\n", encoding="utf-8")
        good_arg = good.relative_to(ROOT).as_posix()
        bad_arg = bad.relative_to(ROOT).as_posix()
        good_result = run([bash, "scripts/check.sh", "--strict", good_arg])
        bad_result = run([bash, "scripts/check.sh", "--strict", bad_arg])
        audit.check(
            good_result.returncode == 0 and bad_result.returncode == 1,
            "check.shは正常本文を許可し、確定違反をstrictで拒否",
            "check.shの終了コード不整合 "
            f"(good={good_result.returncode}, bad={bad_result.returncode})\n"
            f"[good]\n{good_result.stdout}\n[bad]\n{bad_result.stdout}",
        )
        chars_good = run([bash, "scripts/chars.sh", good_arg])
        chars_missing = run([bash, "scripts/chars.sh", f"{good_arg}.missing"])
        audit.check(
            chars_good.returncode == 0
            and "字" in chars_good.stdout
            and chars_missing.returncode == 2,
            "chars.shは文字数を返し、入力欠落を検査不能として拒否",
            "chars.shの終了コード不整合 "
            f"(good={chars_good.returncode}, missing={chars_missing.returncode})",
        )

        fixture = temp / "init-fixture"
        (fixture / "scripts").mkdir(parents=True)
        shutil.copy2(ROOT / "scripts/init-work.sh", fixture / "scripts/init-work.sh")
        shutil.copytree(ROOT / "templates", fixture / "templates")
        first = run([bash, "scripts/init-work.sh"], cwd=fixture)
        plot = fixture / "work/plot.md"
        marker = "\n<!-- audit-preserve -->\n"
        if plot.exists():
            with plot.open("a", encoding="utf-8") as handle:
                handle.write(marker)
        second = run([bash, "scripts/init-work.sh"], cwd=fixture)
        expected = (
            fixture / "work/continuity/current-state.md",
            fixture / "world-bible/00-INDEX.md",
            fixture / "world-bible/core/08-timeline.md",
            fixture / "world-bible/log/canon-log.md",
        )
        preserved = plot.exists() and marker.strip() in plot.read_text(encoding="utf-8")
        audit.check(
            first.returncode == 0
            and second.returncode == 0
            and all(path.exists() for path in expected)
            and preserved,
            "init-work.shは必要構成を生成し、再実行でも既存設計を保持",
            "init-work.shの生成・冪等性テスト失敗\n" + first.stdout + second.stdout,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--static",
        action="store_true",
        help="一時ディレクトリを使うcheck.sh・init-work.sh実行テストを省略する",
    )
    parser.add_argument(
        "--no-dist",
        action="store_true",
        help="配布zipの検査を省略する（zipを作り直す直前に使う）",
    )
    args = parser.parse_args()

    audit = Audit()
    audit_layout(audit)
    audit_skills(audit)
    audit_skill_budget(audit)
    audit_markdown_links(audit)
    audit_source_syntax(audit)
    audit_python_smoke(audit)
    if not args.static:
        audit_executable_workflows(audit)
        if not args.no_dist:
            audit_distribution(audit)

    print()
    print(f"結果: PASS {audit.passes} / WARN {len(audit.warnings)} / FAIL {len(audit.failures)}")
    if audit.failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
