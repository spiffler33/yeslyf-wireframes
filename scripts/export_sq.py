#!/usr/bin/env python3
"""Export the answered questionnaires back in Spinach's layout (phase 14, pass 4; Vatsal, 24 Sep 2026).

For every file of the batch in data/questions.json, one xlsx under docs/exports/ (SQ1_<original name>.xlsx): the
workbook rebuilt sheet for sheet in the original order with the original sheet names, every original row and cell
as Spinach wrote it (read from the file in inputs/spinach/<date>/ with the standard library), the Yesly Comments
column filled with the answer of each question row, then three added columns on every header row and question row:
"Status" (the word, plus the "to be decided:" or "to be verified:" item of an open or owed row), "Board ref" (the refs,
comma separated) and "Changed since <date of the previous export>" ("yes" or blank; blank everywhere on the first
export). Journey sheets keep their blocks and block headers as rows, so the reader sees the shape of the file they
sent; merged cells and Spinach's styling are not reproduced. The summary sheet, which has no Yesly Comments column,
gets one after its last column.

Standard library only: an xlsx is a zip of XML (workbook, worksheets with inline strings, one styles part with a bold
font for header rows and wrapped text for the comment column, the rels and content types). Every written file is
read back with import_questions.read_sheet and compared with the data: sheet names, row counts, every answer and
status cell; a mismatch fails the build.

The export date: the files are rebuilt on every build, but the date stamped on the batch and on every row (exported)
moves only when a row changed since the last stamp (a row's changed date later than the batch's exported date), so a
rebuild on a quiet day keeps the previous export date and its "changed since" marks. On a new stamp the previous
date becomes the "Changed since" column, and a row whose changed date is later than it reads "yes". Called from
scripts/build_site.py before build_questions (the tab shows the download links and the date); also runs alone.
"""
import datetime
import json
import os
import sys
import zipfile
from xml.sax.saxutils import escape, quoteattr

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
from import_questions import read_sheet  # noqa: E402
from import_sq import workbook_sheets, INPUT_DIR  # noqa: E402

DATA_FILE = os.path.join(ROOT, "data", "questions.json")
OUT_DIR = os.path.join(ROOT, "docs", "exports")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
COMMENT_HEADER = "Yesly Comments"
STATUS_HEADER = "Status"
REF_HEADER = "Board ref"
MARKERS = {"open": "to be decided", "owed": "to be verified"}
HEADER_STYLE, WRAP_STYLE = 1, 2
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def dmy(iso):
    return "%d %s %s" % (int(iso[8:10]), MONTHS[int(iso[5:7]) - 1], iso[:4])


def col_letter(i):
    """0-based column index to A, B, ..., Z, AA, ..."""
    s = ""
    i += 1
    while i:
        i, rem = divmod(i - 1, 26)
        s = chr(65 + rem) + s
    return s


def status_text(r):
    if r["status"] == "frozen":
        return "frozen"
    item = r.get("item", "")
    return "%s - %s%s" % (r["status"], MARKERS[r["status"]], (": " + item) if item else "")


def changed_header(previous, today):
    return "Changed since %s" % dmy(previous) if previous else "Changed since previous export (first export %s)" % dmy(today)


def sheet_grid(rows, qrows, previous, today):
    """The output grid of one sheet: the original rows, the comments filled, the added columns; plus the style per cell
    (header rows bold, comment cells wrapped) and which cells were written for the read-back check."""
    grid = [list(r) for r in rows]
    ncol = max(len(r) for r in rows) if rows else 0
    styles = {}
    written = []
    header_rows = sorted({q["header_row"] for q in qrows if q["block"] != "H"})
    needs_comment_col = any(q["comment_col"] < 0 for q in qrows)
    add_at = ncol + (1 if needs_comment_col else 0)

    def put(row_no, col, text, style=None):
        row = grid[row_no - 1]
        while len(row) <= col:
            row.append("")
        row[col] = text
        if style is not None:
            styles[(row_no, col)] = style

    for hr in header_rows:
        if needs_comment_col:
            put(hr, ncol, COMMENT_HEADER, HEADER_STYLE)
        put(hr, add_at, STATUS_HEADER, HEADER_STYLE)
        put(hr, add_at + 1, REF_HEADER, HEADER_STYLE)
        put(hr, add_at + 2, changed_header(previous, today), HEADER_STYLE)
        for c in range(len(grid[hr - 1])):
            if grid[hr - 1][c] and (hr, c) not in styles:
                styles[(hr, c)] = HEADER_STYLE
    for q in qrows:
        ccol = q["comment_col"] if q["comment_col"] >= 0 else ncol
        put(q["row_no"], ccol, q["answer"], WRAP_STYLE)
        put(q["row_no"], add_at, status_text(q), WRAP_STYLE)
        put(q["row_no"], add_at + 1, ", ".join(q["refs"]))
        put(q["row_no"], add_at + 2, "yes" if (previous and q["changed"] > previous) else "")
        written.append((q["id"], q["row_no"], ccol, q["answer"], add_at, status_text(q)))
    widths = {}
    for q in qrows:
        widths[q["comment_col"] if q["comment_col"] >= 0 else ncol] = 60
    widths[add_at] = 44
    return grid, styles, written, widths


def sheet_xml(grid, styles, widths):
    parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
             '<worksheet xmlns="%s" xmlns:r="%s">' % (NS_MAIN, NS_REL)]
    if widths:
        parts.append("<cols>" + "".join('<col min="%d" max="%d" width="%d" customWidth="1"/>' % (c + 1, c + 1, w) for c, w in sorted(widths.items())) + "</cols>")
    parts.append("<sheetData>")
    for i, row in enumerate(grid, 1):
        cells = []
        for j, text in enumerate(row):
            if text == "":
                continue
            style = styles.get((i, j))
            s_attr = (' s="%d"' % style) if style else ""
            cells.append('<c r="%s%d" t="inlineStr"%s><is><t xml:space="preserve">%s</t></is></c>' % (col_letter(j), i, s_attr, escape(text)))
        if not cells:  # an empty row keeps its place: one empty inline cell, so the read-back (and Spinach) sees the same row numbers
            cells.append('<c r="A%d" t="inlineStr"><is><t></t></is></c>' % i)
        parts.append('<row r="%d">%s</row>' % (i, "".join(cells)))
    parts.append("</sheetData></worksheet>")
    return "".join(parts)


STYLES_XML = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<styleSheet xmlns="%s">'
              '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
              '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
              '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
              '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
              '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
              '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
              '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf></cellXfs>'
              '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
              '</styleSheet>') % NS_MAIN


def write_xlsx(path, sheets, stamp):
    """sheets: [(name, xml)] in order. stamp: (y, m, d) used as every entry's time, so an unchanged export is byte-identical."""
    n = len(sheets)
    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="%s" xmlns:r="%s"><sheets>%s</sheets></workbook>' % (
                    NS_MAIN, NS_REL, "".join('<sheet name=%s sheetId="%d" r:id="rId%d"/>' % (quoteattr(name), i, i) for i, (name, _) in enumerate(sheets, 1))))
    wb_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">%s'
               '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
               '</Relationships>' % ("".join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i, i) for i in range(1, n + 1)), n + 1))
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>')
    types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="xml" ContentType="application/xml"/>'
             '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
             '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>%s'
             '</Types>' % "".join('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % i for i in range(1, n + 1)))
    entries = [("[Content_Types].xml", types), ("_rels/.rels", rels), ("xl/workbook.xml", workbook), ("xl/_rels/workbook.xml.rels", wb_rels), ("xl/styles.xml", STYLES_XML)]
    entries += [("xl/worksheets/sheet%d.xml" % i, xml) for i, (_, xml) in enumerate(sheets, 1)]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in entries:
            info = zipfile.ZipInfo(name, date_time=(stamp[0], stamp[1], stamp[2], 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, text.encode("utf-8"))


def verify(path, original_sheets, written_by_sheet, problems):
    """Read the file back: the sheet names in order, the row counts, every answer and status cell."""
    back = workbook_sheets(path)
    if [n for n, _ in back] != [n for n, _ in original_sheets]:
        problems.append("%s: sheet names differ from the original: %r" % (os.path.basename(path), [n for n, _ in back]))
        return
    for (name, n), (_, n_orig) in zip(back, original_sheets):
        rows = read_sheet(path, n)
        expect_rows, written = written_by_sheet[name]
        if len(rows) != expect_rows:
            problems.append("%s %r: %d rows read back, %d expected" % (os.path.basename(path), name, len(rows), expect_rows))
        for rid, row_no, ccol, answer, scol, stext in written:
            row = rows[row_no - 1] if row_no - 1 < len(rows) else []
            got = row[ccol] if ccol < len(row) else ""
            if got != answer:
                problems.append("%s: the comment cell of %s (row %d) reads back differently" % (os.path.basename(path), rid, row_no))
            got_s = row[scol] if scol < len(row) else ""
            if got_s != stext:
                problems.append("%s: the status cell of %s (row %d) reads back %r" % (os.path.basename(path), rid, row_no, got_s))


def main(argv=()):
    today = datetime.date.today().isoformat()
    for i, a in enumerate(argv):
        if a == "--date" and i + 1 < len(argv):
            today = argv[i + 1]
    with open(DATA_FILE) as fh:
        doc = json.load(fh)
    batch = doc["batches"][0]
    rows = doc["rows"]
    previous_stamp = batch.get("exported", "")
    restamp = (not previous_stamp) or any(r["changed"] > previous_stamp for r in rows)
    if restamp:
        batch["exported_previous"] = previous_stamp
        batch["exported"] = today
        for r in rows:
            r["exported"] = today
    exported, previous = batch["exported"], batch.get("exported_previous", "")
    stamp = tuple(int(x) for x in exported.split("-"))
    os.makedirs(OUT_DIR, exist_ok=True)
    problems, summary = [], []
    for f in batch["files"]:
        src = os.path.join(INPUT_DIR, f["name"])
        original_sheets = workbook_sheets(src)
        sheets, written_by_sheet, filled = [], {}, 0
        for name, n in original_sheets:
            orig_rows = read_sheet(src, n)
            qrows = sorted([r for r in rows if r["file"] == f["name"] and r["sheet"] == name], key=lambda r: r["row_no"])
            grid, styles, written, widths = sheet_grid(orig_rows, qrows, previous, exported)
            sheets.append((name, sheet_xml(grid, styles, widths)))
            written_by_sheet[name] = (len(orig_rows), written)
            filled += len(written)
        path = os.path.join(OUT_DIR, f["export"])
        write_xlsx(path, sheets, stamp)
        verify(path, original_sheets, written_by_sheet, problems)
        expected = sum(1 for r in rows if r["file"] == f["name"])
        if filled != expected:
            problems.append("%s: %d comments written, %d rows in the data" % (f["export"], filled, expected))
        summary.append((f["export"], len(sheets), filled, os.path.getsize(path)))
    if problems:
        for p in problems:
            print("ERROR: " + p)
        sys.exit(1)
    with open(DATA_FILE, "w") as fh:
        fh.write(json.dumps(doc, indent=1, ensure_ascii=True) + "\n")
    for name, n_sheets, filled, size in summary:
        print("wrote docs/exports/%s (%d bytes, %d sheets, %d comments filled)" % (name, size, n_sheets, filled))
    print("export date %s%s; changed since: %s" % (exported, " (new stamp)" if restamp else " (unchanged since the last stamp)", dmy(previous) if previous else "first export, no marks"))


if __name__ == "__main__":
    main(sys.argv[1:])
