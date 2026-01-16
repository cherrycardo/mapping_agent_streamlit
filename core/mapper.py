import pandas as pd

def classify_table(df: pd.DataFrame) -> str:
    headers = " ".join([str(c).lower() for c in df.columns])

    # Heuristics
    mapping_keywords = ["source", "raw", "bronze", "column", "field"]
    design_keywords = ["table name", "definition", "layer", "raw table", "bronze table"]

    score_mapping = sum(k in headers for k in mapping_keywords)
    score_design = sum(k in headers for k in design_keywords)

    if score_mapping >= 3 and "raw" in headers and "bronze" in headers:
        return "table_mapping"
    if score_design >= 2 and "table" in headers:
        return "table_design"
    return "other"