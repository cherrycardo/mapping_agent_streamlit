def validate_rows(rows: list[dict]) -> list[str]:
    issues = []
    for i, r in enumerate(rows, start=1):
        if not r.get("source_field"):
            issues.append(f"Row {i}: missing source_field")
        if not r.get("raw_column"):
            issues.append(f"Row {i}: missing raw_column")
        if not r.get("bronze_column"):
            issues.append(f"Row {i}: missing bronze_column")
    return issues