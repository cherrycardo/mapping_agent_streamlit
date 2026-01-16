import streamlit as st
import tempfile
import os

from core.docx_mapping_table import extract_raw_bronze_pairs_from_mapping_table
from core.excel_writer import append_raw_bronze_to_template

st.set_page_config(page_title="Raw to Bronze Mapping Agent", layout="wide")
st.title("Raw to Bronze Mapping Agent")

template_path = "templates/Master Mapping Template (2).xlsx"
sheet_name = "Source to Raw to Bronze"

raw_table_name = "raw_cpm_customer_profile_event_compliance"
bronze_table_name = "stg_cpm_customer_profile_event_compliance"

uploaded = st.file_uploader("Upload requirements Word doc (DOCX)", type=["docx"])

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded.read())
        docx_path = tmp.name

    st.success("DOCX uploaded.")

    if st.button("Generate Excel mapping"):
        try:
            pairs = extract_raw_bronze_pairs_from_mapping_table(
                docx_path=docx_path,
                raw_header=raw_table_name,
                bronze_header=bronze_table_name,
            )

            st.write(f"Extracted {len(pairs)} raw to bronze column pairs.")
            st.dataframe(pairs[:50])

            out_path = os.path.join(tempfile.gettempdir(), "Generated_Mapping.xlsx")

            append_raw_bronze_to_template(
                template_path=template_path,
                output_path=out_path,
                sheet_name=sheet_name,
                raw_table_name=raw_table_name,
                bronze_table_name=bronze_table_name,
                pairs=pairs,
            )

            with open(out_path, "rb") as f:
                st.download_button(
                    "Download generated Excel mapping",
                    f,
                    file_name="Generated_Mapping.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        except Exception as e:
            st.error(str(e))

