from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "prompts" / "weekly_report_prompt.md"
WEEKLY_CONTEXT_DIR = ROOT / "contexts" / "weekly"
WEEKLY_DIR = ROOT / "weekly"


def get_week_id() -> str:
    today = datetime.now()
    year, week, _ = today.isocalendar()
    return f"{year}-W{week:02d}"


def main() -> None:
    week_id = get_week_id()

    context_path = WEEKLY_CONTEXT_DIR / f"{week_id}_context.md"
    report_path = WEEKLY_DIR / f"{week_id}.md"

    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)

    if not context_path.exists():
        raise FileNotFoundError(f"Weekly context file not found: {context_path}")

    base_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    prompt = f"""
{base_prompt}

# 입력 파일

{context_path.as_posix()}

# 출력 파일

{report_path.as_posix()}

# 실행 지시

1. 입력 파일을 읽는다.
2. 월~금 일일 연구노트를 통합한다.
3. 중복 항목은 하나로 합친다.
4. 상급자 보고용 주간보고서를 작성한다.
5. 출력 파일 외 업무 프로젝트 파일은 수정하지 않는다.
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

    print(report_path)


if __name__ == "__main__":
    main()