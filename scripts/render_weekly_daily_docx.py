from __future__ import annotations

import copy
import re
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "templates" / "word" / "daily_note_template.docx"
NOTES_DIR = ROOT / "notes"
DOCX_DIR = ROOT / "documents" / "daily_note"
LATEST_PATH = DOCX_DIR / "latest_daily_note_docx_path.txt"

WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", WORD_NS)


def w_tag(name: str) -> str:
    return f"{{{WORD_NS}}}{name}"


def week_range(today: datetime | None = None) -> tuple[datetime, datetime]:
    if today is None:
        today = datetime.now()

    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday


def iter_weekdays(start: datetime, end: datetime):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def note_path_for_date(date_obj: datetime) -> Path:
    date_str = date_obj.strftime("%Y-%m-%d")
    weekday_kr = WEEKDAY_KR[date_obj.weekday()]
    return NOTES_DIR / f"{date_str}_{weekday_kr}.md"


def compact_text(text: str, max_chars: int) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 1].rstrip() + "…"


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)
    text = text.replace("|", " ")
    return compact_text(text, 4000)


def extract_section(markdown_text: str, keywords: list[str], fallback_chars: int) -> str:
    lines = markdown_text.splitlines()
    capture = False
    captured: list[str] = []

    for line in lines:
        stripped = line.strip()
        heading = re.match(r"^#{1,6}\s*(.+)$", stripped)
        if heading:
            heading_text = heading.group(1).strip()
            if capture:
                break
            capture = any(keyword in heading_text for keyword in keywords)
            continue

        if capture:
            captured.append(line)

    source = "\n".join(captured).strip() if captured else markdown_text
    return compact_text(strip_markdown(source), fallback_chars)


def summarize_daily_note(markdown_text: str, date_obj: datetime) -> dict[str, str]:
    date_label = date_obj.strftime("%Y-%m-%d")
    weekday_kr = WEEKDAY_KR[date_obj.weekday()]
    fallback = strip_markdown(markdown_text)

    title = extract_section(markdown_text, ["연구제목", "제목", "Title"], 80)
    if title == fallback:
        title = f"{date_label} ({weekday_kr}) 일일 연구노트"

    purpose = extract_section(markdown_text, ["목적", "연구 목적", "Purpose"], 160)
    plan = extract_section(markdown_text, ["계획", "연구계획", "Plan"], 220)
    process = extract_section(markdown_text, ["과정", "수행", "진행", "내용", "Process"], 520)
    result = extract_section(markdown_text, ["결과", "성과", "Result"], 300)

    if purpose == fallback:
        purpose = compact_text(fallback, 160)
    if plan == fallback:
        plan = "당일 생성된 연구노트 내용을 기반으로 주요 수행 항목을 요약함."
    if process == fallback:
        process = compact_text(fallback, 520)
    if result == fallback:
        result = "당일 연구노트 참조."

    return {
        "title": title,
        "purpose": purpose,
        "plan": plan,
        "process": process,
        "result": result,
    }


def empty_daily_note_summary(date_obj: datetime) -> dict[str, str]:
    date_label = date_obj.strftime("%Y-%m-%d")
    weekday_kr = WEEKDAY_KR[date_obj.weekday()]
    return {
        "title": f"{date_label} ({weekday_kr}) 일일 연구노트",
        "purpose": "해당 일자의 일일 연구노트가 아직 생성되지 않음.",
        "plan": "미생성",
        "process": "미생성",
        "result": "미생성",
    }


def make_daily_summary(date_obj: datetime) -> dict[str, str]:
    note_path = note_path_for_date(date_obj)
    if not note_path.exists():
        return empty_daily_note_summary(date_obj)

    markdown_text = note_path.read_text(encoding="utf-8", errors="replace")
    return summarize_daily_note(markdown_text, date_obj)


def paragraph(text: str = "") -> ET.Element:
    p = ET.Element(w_tag("p"))
    if not text:
        return p

    lines = text.splitlines() or [""]
    for index, line in enumerate(lines):
        r = ET.SubElement(p, w_tag("r"))
        if index:
            ET.SubElement(r, w_tag("br"))
        t = ET.SubElement(r, w_tag("t"))
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = line
    return p


def page_break() -> ET.Element:
    p = ET.Element(w_tag("p"))
    r = ET.SubElement(p, w_tag("r"))
    br = ET.SubElement(r, w_tag("br"))
    br.set(w_tag("type"), "page")
    return p


def clear_cell_text(cell: ET.Element) -> None:
    for child in list(cell):
        if child.tag == w_tag("p"):
            cell.remove(child)


def set_cell_text(cell: ET.Element, text: str) -> None:
    clear_cell_text(cell)
    for block in text.split("\n\n"):
        cell.append(paragraph(block.strip()))


def table_rows(table: ET.Element) -> list[ET.Element]:
    return [child for child in table if child.tag == w_tag("tr")]


def row_cells(row: ET.Element) -> list[ET.Element]:
    return [child for child in row if child.tag == w_tag("tc")]


def fill_contents_table(contents_table: ET.Element, summaries: list[dict[str, str]]) -> None:
    rows = table_rows(contents_table)
    if len(rows) < 2:
        raise RuntimeError("Contents of Study table must contain a header row and one template row.")

    template_row = copy.deepcopy(rows[1])
    for row in rows[1:]:
        contents_table.remove(row)

    for index, summary in enumerate(summaries, start=1):
        row = copy.deepcopy(template_row)
        cells = row_cells(row)
        if len(cells) >= 3:
            set_cell_text(cells[0], str(index))
            set_cell_text(cells[1], summary["purpose"])
            set_cell_text(cells[2], summary["title"])
        contents_table.append(row)


def fill_daily_page_table(page_table: ET.Element, summary: dict[str, str], date_obj: datetime) -> ET.Element:
    table = copy.deepcopy(page_table)
    rows = table_rows(table)

    if rows:
        cells = row_cells(rows[0])
        if cells:
            content = (
                f"연구제목: {summary['title']}\n"
                f"연구목적: {summary['purpose']}\n"
                "연구계획\n"
                f"{summary['plan']}\n\n"
                "연구과정\n"
                f"{summary['process']}\n\n"
                "연구결과\n"
                f"{summary['result']}\n\n"
                "Continued from page :"
            )
            set_cell_text(cells[0], content)

    if len(rows) >= 3:
        cells = row_cells(rows[2])
        if cells:
            set_cell_text(cells[0], f"일자 Date\n{date_obj.strftime('%Y-%m-%d')}")

    return table


def update_document(template_path: Path, output_path: Path, monday: datetime, friday: datetime) -> None:
    summaries = [make_daily_summary(date_obj) for date_obj in iter_weekdays(monday, friday)]

    with TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        working_docx = tmp_dir / "working.docx"
        shutil.copy2(template_path, working_docx)

        with zipfile.ZipFile(working_docx, "r") as src:
            src.extractall(tmp_dir / "docx")

        document_xml_path = tmp_dir / "docx" / "word" / "document.xml"
        tree = ET.parse(document_xml_path)
        root = tree.getroot()
        body = root.find(w_tag("body"))
        if body is None:
            raise RuntimeError("Template document.xml does not contain a Word body.")

        tables = body.findall(f".//{w_tag('tbl')}")
        if len(tables) < 3:
            raise RuntimeError("Template must contain checklist, Contents of Study, and daily page tables.")

        contents_table = tables[1]
        daily_page_template = tables[2]
        fill_contents_table(contents_table, summaries)

        sect_pr = body.find(w_tag("sectPr"))
        if sect_pr is not None:
            body.remove(sect_pr)

        body.remove(daily_page_template)

        for index, date_obj in enumerate(iter_weekdays(monday, friday)):
            body.append(page_break())
            body.append(fill_daily_page_table(daily_page_template, summaries[index], date_obj))

        if sect_pr is not None:
            body.append(sect_pr)

        tree.write(document_xml_path, encoding="utf-8", xml_declaration=True)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            output_path.unlink()

        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as dst:
            for file_path in (tmp_dir / "docx").rglob("*"):
                if file_path.is_file():
                    dst.write(file_path, file_path.relative_to(tmp_dir / "docx").as_posix())


def main() -> None:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Word template not found: {TEMPLATE_PATH}")

    monday, friday = week_range()
    output_name = f"{monday.strftime('%Y%m%d')}~{friday.strftime('%Y%m%d')}_daily_note.docx"
    output_path = DOCX_DIR / output_name

    update_document(TEMPLATE_PATH, output_path, monday, friday)

    LATEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    LATEST_PATH.write_text(str(output_path), encoding="utf-8")

    print(output_path)


if __name__ == "__main__":
    main()
