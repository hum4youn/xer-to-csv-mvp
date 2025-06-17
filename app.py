import streamlit as st
import pandas as pd
from xer_parser import parse_xer
import io

st.title("Primavera XER to CSV Converter")

uploaded_file = st.file_uploader("Upload your XER file", type=["xer"])
if uploaded_file:
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    tables = parse_xer(content)

    for name, df in tables.items():
        st.subheader(name)
        st.dataframe(df.head())
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(f"Download {name}.csv", csv, file_name=f"{name}.csv", mime="text/csv")
