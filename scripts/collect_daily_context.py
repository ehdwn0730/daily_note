from __future__ import annotations

import fnmatch
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "projects.yaml"
CONTEXT_DIR = ROOT / "contexts"

MAX_DIFF_CHARS_PER_PROJECT = 15000
MAX_INCLUDED_FILE_CHARS = 6000


SENSITIVE_PATTERNS = [
    (re.compile(r"(?i)(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*[^\s]+"), r"\1=[MASKED]"),
    (re.compile(r"(?i)(host|server)\s*[:=]\s*\d{1,3}(?:\.\d{1,3}){3}"), r"\1=[MASKED_IP]"),
    (re.compile(r"(?i)(user|username)\s*[:=]\s*[^\s]+"), r"\1=[MASKED_USER]"),
]


def mask_sensitive(text: str) -> str:
    masked = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked


def run_cmd(cmd: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        output = result.stdout.strip() or result.stderr.strip() or "[NO_OUTPUT]"
        return mask_sensitive(output)
    except Exception as e:
        return f"[ERROR] command failed: {' '.join(cmd)} / {e}"


def today_info() -> tuple[str, str]:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][now.weekday()]
    return date_str, weekday_kr


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def should_exclude(path_text: str, patterns: list[str]) -> bool:
    normalized = path_text.replace("\\", "/")
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def read_file_limited(path: Path, max_chars: int = MAX_INCLUDED_FILE_CHARS) -> str:
    if not path.exists():
        return "[NOT_FOUND]"

    if path.is_dir():
        return "[SKIPPED_DIRECTORY]"

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return mask_sensitive(text[:max_chars])
    except Exception as e:
        return f"[ERROR] failed to read file: {e}"


def collect_git_context(project_path: Path) -> dict[str, str]:
    return {
        "status": run_cmd(["git", "status", "--short"], project_path),
        "log_24h": run_cmd(
            [
                "git",
                "log",
                "--since=24 hours ago",
                "--pretty=format:%h | %an | %ad | %s",
                "--date=iso",
            ],
            project_path,
        ),
        "diff_stat": run_cmd(["git", "diff", "--stat"], project_path),
        "diff": run_cmd(["git", "diff", "--unified=3"], project_path)[:MAX_DIFF_CHARS_PER_PROJECT],
        "staged_diff_stat": run_cmd(["git", "diff", "--cached", "--stat"], project_path),
        "staged_diff": run_cmd(["git", "diff", "--cached", "--unified=3"], project_path)[:MAX_DIFF_CHARS_PER_PROJECT],
        "untracked_files": run_cmd(["git", "ls-files", "--others", "--exclude-standard"], project_path),
    }



def collect_project_section(project: dict[str, Any]) -> str:
    name = project["name"]
    path = Path(project["path"])
    include_files = project.get("include_files", [])
    exclude_patterns = project.get("exclude_patterns", [])

    if not path.exists():
        return f"""
            ## {name}

            ### 상태

            프로젝트 경로를 찾을 수 없습니다.

            ```text
            {path}
            ```
        """