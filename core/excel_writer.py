from openpyxl import load_workbook

def _norm(s) -> str:
    return " ".join(str(s or "").strip().lower().split())

def _find_header_row(ws, must_contain: list[str], max_rows: int = 30):
    must = [_norm(x) for x in must_contain]
    for r in range(1, max_rows + 1):
        row_vals = [_norm(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)]
        if all(m in row_vals for m in must):
            return r, row_vals
    return None, None

def append_raw_bronze_to_template(
    template_path: str,
    output_path: str,
    sheet_name: str,
    raw_table_name: str,
    bronze_table_name: str,
    pairs: list[dict],
):
    wb = load_workbook(template_path)
    ws = wb[sheet_name]

    # These are the exact headers that exist in your template in row 2.
    header_row, header_vals = _find_header_row(
        ws,
        must_contain=["Raw table name", "Raw column name", "Table Name", "Column Name"],
    )
    if not header_row:
        raise ValueError(f"Could not find expected headers in sheet: {sheet_name}")

    # Build a map: header text -> column index
    header_to_col = {}
    for c, h in enumerate(header_vals, start=1):
        if h:
            header_to_col[h] = c

    def col(header_text: str) -> int:
        key = _norm(header_text)
        if key not in header_to_col:
            raise ValueError(f"Missing header in template: {header_text}")
        return header_to_col[key]

    # Find first empty row after header
    r = header_row + 1
    while True:
        # Use Raw column name as the anchor for "is this row empty"
        if ws.cell(r, col("Raw column name")).value in (None, ""):
            break
        r += 1

    for p in pairs:
        ws.cell(r, col("Raw table name")).value = raw_table_name
        ws.cell(r, col("Raw column name")).value = p.get("raw_column", "")

        # In this template, Bronze uses:
        # Table Name = Bronze table name
        # Column Name = Bronze column name
        ws.cell(r, col("Table Name")).value = bronze_table_name
        ws.cell(r, col("Column Name")).value = p.get("bronze_column", "")

        r += 1

    wb.save(output_path)
