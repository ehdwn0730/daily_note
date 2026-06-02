from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = ROOT / "notes"
WEEKLY_CONTEXT_DIR = ROOT / "contexts" / "weekly"

WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]


def get_week_range(today: datetime | None = None) -> tuple[datetime, datetime]:
    if today is None:
        today = datetime.now()

    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday


def week_id_from_date(date_obj: datetime) -> str:
    year, week, _ = date_obj.isocalendar()
    return f"{year}-W{week:02d}"


def note_path_for_date(date_obj: datetime) -> Path:
    date_str = date_obj.strftime("%Y-%m-%d")
    weekday_kr = WEEKDAY_KR[date_obj.weekday()]
    return NOTES_DIR / f"{date_str}_{weekday_kr}.md"


def main() -> None:
    monday, friday = get_week_range()
    week_id = week_id_from_date(monday)

    WEEKLY_CONTEXT_DIR.mkdir(parents=True, exist_ok=True)

    sections = []
    current = monday

    while current <= friday:
        path = note_path_for_date(current)
        date_str = current.strftime("%Y-%m-%d")
        weekday_kr = WEEKDAY_KR[current.weekday()]

        if path.exists():
            content = path.read_text(encoding="utf-8", errors="replace")
        else:
            content = "[NOT_FOUND] 해당 날짜의 일일 연구노트가 없습니다."

        sections.append(
            f"""
                ## {date_str} {weekday_kr}요일

                Source: {path.as_posix()}

                ```markdown
                {content}
                ```
            """
        )