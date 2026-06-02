from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "prompts" / "daily_note_prompt.md"
CONTEXT_DIR = ROOT / "contexts"
NOTES_DIR = ROOT / "notes"


def today_info() -> tuple[str, str]:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][now.weekday()]
    return date_str, weekday_kr


def main() -> None:
    date_str, weekday_kr = today_info()

    context_path = CONTEXT_DIR / f"{date_str}_{weekday_kr}_context.md"
    note_path = NOTES_DIR / f"{date_str}_{weekday_kr}.md"
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    if not context_path.exists():
        raise FileNotFoundError(f"Context file not found: {context_path}")

    base_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    prompt = f"""
{base_prompt}

# 입력 파일

{context_path.as_posix()}

# 출력 파일

{note_path.as_posix()}

# 실행 지시

1. 입력 파일을 읽는다.
2. 입력 파일에 있는 근거만 사용한다.
3. 출력 파일에 Markdown 연구노트를 생성한다.
4. 출력 파일 외 업무 프로젝트 파일은 수정하지 않는다.
"""

    result = subprocess.run(
        ["codex", "exec", "--sandbox", "workspace-write", prompt],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Codex failed with return code: {result.returncode}")

    print(note_path)


if __name__ == "__main__":
    main()