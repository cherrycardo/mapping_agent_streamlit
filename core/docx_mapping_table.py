from docx import Document

def _norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())

def _table_to_matrix(table):
    # Convert docx table to plain text matrix
    mat = []
    for row in table.rows:
        mat.append([cell.text.strip() for cell in row.cells])
    return mat

def extract_raw_bronze_pairs_from_mapping_table(
    docx_path: str,
    raw_table_name: str,
    bronze_table_name: str,
    title_text: str = "raw->bronze data mapping",
) -> list[dict]:
    """
    Extracts mappings from the DOCX table titled 'Raw->Bronze Data Mapping'.
    Pulls:
      - raw_column from the left-side 'Column Name'
      - bronze_column from the right-side 'Actual Column Name'
    Also optionally returns bronze datatype + description when present.
    """

    doc = Document(docx_path)
    raw_table_name_n = _norm(raw_table_name)
    bronze_table_name_n = _norm(bronze_table_name)
    title_n = _norm(title_text)

    target_mat = None

    # 1) Find the correct table using a robust heuristic:
    #    table contains the title OR contains both table names somewhere in the first few rows.
    for t in doc.tables:
        mat = _table_to_matrix(t)
        if not mat:
            continue

        top_text = " ".join(_norm(x) for row in mat[:4] for x in row if x)
        if (title_n in top_text) or (raw_table_name_n in top_text and bronze_table_name_n in top_text):
            target_mat = mat
            break

    if target_mat is None:
        raise ValueError("Could not find the 'Raw->Bronze Data Mapping' table in the DOCX.")

    # 2) Find the header row that contains the column labels we need
    #    We need a row that has 'column name' on the raw side and 'actual column name' on the bronze side
    header_row_idx = None
    raw_col_idx = None
    bronze_col_idx = None
    bronze_dtype_idx = None
    bronze_desc_idx = None

    for i, row in enumerate(target_mat[:10]):  # scan first 10 rows for headers
        row_n = [_norm(c) for c in row]

        # Identify candidate indices
        if "column name" in row_n and "actual column name" in row_n:
            header_row_idx = i
            raw_col_idx = row_n.index("column name")
            bronze_col_idx = row_n.index("actual column name")

            # Optional fields on bronze side
            if "data type" in row_n:
                # This will pick the first occurrence; good enough for MVP
                bronze_dtype_idx = row_n.index("data type")
            if "description" in row_n:
                bronze_desc_idx = row_n.index("description")
            break

    if header_row_idx is None:
        raise ValueError(
            "Found the mapping table, but could not locate the header row with "
            "'Column Name' and 'Actual Column Name'."
        )

    # 3) Extract data rows after the header
    pairs = []
    for row in target_mat[header_row_idx + 1:]:
        # guard against short rows
        if raw_col_idx >= len(row) or bronze_col_idx >= len(row):
            continue

        raw_col = (row[raw_col_idx] or "").strip()
        bronze_col = (row[bronze_col_idx] or "").strip()

        # skip blank rows
        if not raw_col and not bronze_col:
            continue

        item = {
            "raw_column": raw_col,
            "bronze_column": bronze_col,
        }

        if bronze_dtype_idx is not None and bronze_dtype_idx < len(row):
            item["bronze_datatype"] = (row[bronze_dtype_idx] or "").strip()
        if bronze_desc_idx is not None and bronze_desc_idx < len(row):
            item["bronze_description"] = (row[bronze_desc_idx] or "").strip()

        pairs.append(item)

    return pairs
