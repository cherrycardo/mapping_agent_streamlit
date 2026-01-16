from docx import Document

def _norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())

def extract_raw_bronze_pairs(
    docx_path: str,
    raw_header: str,
    bronze_header: str,
    title_text: str = "Raw->Bronze Data Mapping",
    section_text: str = "Data Mappings",
) -> list[dict]:
    """
    Returns a list of dicts:
      { "raw_column": "...", "bronze_column": "..." }

    Heuristic:
    - Prefer a table that has a row containing the title_text nearby.
    - Must contain both expected headers in its first row.
    """

    doc = Document(docx_path)

    expected_raw = _norm(raw_header)
    expected_bronze = _norm(bronze_header)

    # Collect nearby paragraph text for each table by scanning document in order.
    # python-docx does not give perfect "table under heading" info, so we use heuristics:
    # If the table header row matches, it is the one.
    best_match_table = None

    for table in doc.tables:
        if not table.rows:
            continue

        header_cells = [ _norm(cell.text) for cell in table.rows[0].cells ]
        if expected_raw in header_cells and expected_bronze in header_cells:
            best_match_table = table
            break

    if best_match_table is None:
        raise ValueError(
            "Could not find a table whose header row contains both:\n"
            f"{raw_header}\n{bronze_header}\n"
            "Confirm the exact header text in the Word table."
        )

    header_cells = [ _norm(cell.text) for cell in best_match_table.rows[0].cells ]
    raw_idx = header_cells.index(expected_raw)
    bronze_idx = header_cells.index(expected_bronze)

    pairs = []
    for r in range(1, len(best_match_table.rows)):
        row = best_match_table.rows[r]
        raw_val = (row.cells[raw_idx].text or "").strip()
        bronze_val = (row.cells[bronze_idx].text or "").strip()

        # Skip blank lines
        if not raw_val and not bronze_val:
            continue

        pairs.append({
            "raw_column": raw_val,
            "bronze_column": bronze_val,
        })

    return pairs
