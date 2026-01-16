from docx import Document
import pandas as pd

def extract_all_tables(docx_path: str) -> list[pd.DataFrame]:
    doc = Document(docx_path)
    dfs = []

    for table in doc.tables:
        data = []
        for row in table.rows:
            data.append([cell.text.strip() for cell in row.cells])

        # Skip empty tables
        if not data or len(data) < 2:
            continue

        # Use first row as header
        header = data[0]
        rows = data[1:]

        df = pd.DataFrame(rows, columns=header)
        # Drop fully empty columns
        df = df.dropna(axis=1, how="all")
        dfs.append(df)

    return dfs