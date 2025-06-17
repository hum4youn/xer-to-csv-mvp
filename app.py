import streamlit as st
import pandas as pd
from xer_parser import parse_xer
import io

st.title("Primavera XER to CSV Converter")

uploaded_file = st.file_uploader("Upload your XER file", type=["xer"])
if uploaded_file:
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    tables = parse_xer(content)

    # Preview each table
    for name, df in tables.items():
        st.subheader(name)
        st.dataframe(df.head())
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(f"Download {name}.csv", csv, file_name=f"{name}.csv", mime="text/csv")

    # 👉 Combine all into a single Excel file
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        for name, df in tables.items():
            safe_name = name[:31]  # Excel sheet name limit
            df.to_excel(writer, sheet_name=safe_name, index=False)
        writer.save()
    st.download_button(
        "📥 Download All as Excel",
        data=excel_buffer.getvalue(),
        file_name="xer_tables.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
