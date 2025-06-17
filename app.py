import streamlit as st
import pandas as pd
import io
from xer_parser import parse_xer  # your custom parser

st.set_page_config(page_title="XER to CSV Converter", layout="wide")
st.title("📊 Primavera XER to CSV + Excel Converter")

uploaded_file = st.file_uploader("📁 Upload your XER file", type=["xer"])

if uploaded_file:
    content = uploaded_file.read().decode("utf-8", errors="ignore")

    # Parse XER file into tables
    tables = parse_xer(content)

    # Show and offer CSV download per table
    for name, df in tables.items():
        st.subheader(f"🧾 {name}")
        st.dataframe(df.head())
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"⬇️ Download {name}.csv",
            data=csv_data,
            file_name=f"{name}.csv",
            mime="text/csv"
        )

    # Create single Excel file with all sheets
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        for name, df in tables.items():
            safe_name = name[:31]  # Excel sheet name limit
            df.to_excel(writer, sheet_name=safe_name, index=False)

    st.download_button(
        label="📥 Download All Tables as Excel (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name="xer_tables.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
