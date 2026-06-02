from __future__ import annotations

from datetime import datetime
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = ROOT / "notes"
HTML_DIR = ROOT / "html"


WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]


def today_info() -> tuple[str, str]:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    weekday_kr = WEEKDAY_KR[now.weekday()]
    return date_str, weekday_kr


def build_html(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    body {{
      font-family: "Malgun Gothic", Arial, sans-serif;
      margin: 0;
      padding: 40px;
      background: #f6f7f9;
      color: #222;
      line-height: 1.7;
    }}

    .container {{
      max-width: 1100px;
      margin: 0 auto;
      background: #ffffff;
      padding: 40px 48px;
      border-radius: 16px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }}

    h1 {{
      border-bottom: 3px solid #222;
      padding-bottom: 12px;
      margin-bottom: 28px;
    }}

    h2 {{
      margin-top: 36px;
      border-left: 6px solid #555;
      padding-left: 12px;
    }}

    h3 {{
      margin-top: 28px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0 28px 0;
      font-size: 14px;
    }}

    th, td {{
      border: 1px solid #ddd;
      padding: 10px 12px;
      vertical-align: top;
    }}

    th {{
      background: #f0f2f5;
      font-weight: 700;
    }}

    code {{
      background: #f1f1f1;
      padding: 2px 5px;
      border-radius: 4px;
    }}

    pre {{
      background: #1f2937;
      color: #f9fafb;
      padding: 16px;
      border-radius: 10px;
      overflow-x: auto;
    }}

    .meta {{
      color: #666;
      font-size: 14px;
      margin-bottom: 24px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="meta">자동 생성 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
    {body_html}
  </div>
</body>
</html>
"""


def main() -> None:
    date_str, weekday_kr = today_info()

    note_path = NOTES_DIR / f"{date_str}_{weekday_kr}.md"
    html_path = HTML_DIR / f"{date_str}_{weekday_kr}.html"

    if not note_path.exists():
        raise FileNotFoundError(f"Daily note not found: {note_path}")

    HTML_DIR.mkdir(parents=True, exist_ok=True)

    markdown_text = note_path.read_text(encoding="utf-8", errors="replace")

    body_html = markdown.markdown(
        markdown_text,
        extensions=[
            "tables",
            "fenced_code",
            "toc",
        ],
    )

    title = f"일일 연구노트 - {date_str} {weekday_kr}요일"
    html = build_html(title=title, body_html=body_html)

    html_path.write_text(html, encoding="utf-8")

    latest_path = HTML_DIR / "latest_daily_html_path.txt"
    latest_path.write_text(str(html_path), encoding="utf-8")

    print(html_path)


if __name__ == "__main__":
    main()