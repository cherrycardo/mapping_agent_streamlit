import streamlit as st
import tempfile
from core.docx_extractor import extract_all_tables

st.set_page_config(page_title="Mapping Agent", layout="wide")
st.title("Requirements to Mapping Agent (DOCX → Excel)")

uploaded = st.file_uploader("Upload Requirements DOCX", type=["docx"])

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded.read())
        docx_path = tmp.name

    st.success("DOCX uploaded successfully.")

    tables = extract_all_tables(docx_path)
    st.write(f"Found {len(tables)} tables in the document.")

    with st.expander("Preview extracted tables"):
        for i, t in enumerate(tables[:3]):
            st.write(f"Table {i+1}")
            st.dataframe(t)