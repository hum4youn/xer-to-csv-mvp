# FILE: main.py

import streamlit as st
import zipfile
import os
import pandas as pd
from xer_parser import parse_xer_file
from datetime import datetime

# --- CONFIG ---
ROOT_DIR = "XER_DB"
BL_SOURCE_XER = os.path.join(ROOT_DIR, "BL_Source_XER")
BL_CSV_OUTPUTS = os.path.join(ROOT_DIR, "BL_CSV_Outputs")

# --- Ensure folder structure ---
os.makedirs(ROOT_DIR, exist_ok=True)
os.makedirs(BL_SOURCE_XER, exist_ok=True)
os.makedirs(BL_CSV_OUTPUTS, exist_ok=True)

# --- App Title ---
st.title("XER to CSV Batch Processor")

# --- Select Data Date ---
data_date_str = st.text_input("Enter Reporting Data Date (DD-MM-YYYY)")
if data_date_str:
    try:
        datetime.strptime(data_date_str, "%d-%m-%Y")
    except ValueError:
        st.error("Please enter the date in DD-MM-YYYY format")
        st.stop()
    
    OUTPUT_FOLDER = os.path.join(ROOT_DIR, data_date_str, "CSV_Output")
    SOURCE_FOLDER = os.path.join(ROOT_DIR, data_date_str, "Source_XER")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(SOURCE_FOLDER, exist_ok=True)

    uploaded_file = st.file_uploader("Upload a ZIP file of XERs", type="zip")

    if uploaded_file:
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            zip_ref.extractall(SOURCE_FOLDER)
        st.success("Files extracted. Processing...")

        all_dataframes = {}

        for filename in os.listdir(SOURCE_FOLDER):
            if filename.endswith(".xer"):
                xer_path = os.path.join(SOURCE_FOLDER, filename)
                xer_tables = parse_xer_file(xer_path)

                if "PROJECT" not in xer_tables:
                    st.warning(f"PROJECT table not found in {filename}. Skipping.")
                    continue

                for _, proj_row in xer_tables["PROJECT"].iterrows():
                    proj_id = proj_row["proj_id"]
                    data_date = proj_row["last_recalc_date"]

                    for table_name, df in xer_tables.items():
                        if "proj_id" in df.columns:
                            filtered = df[df["proj_id"] == proj_id].copy()
                        else:
                            filtered = df.copy()

                        filtered["proj_id"] = proj_id
                        filtered["DataDate"] = data_date
                        filtered["source_xer_filename"] = filename

                        key = f"{table_name}"
                        if key not in all_dataframes:
                            all_dataframes[key] = [filtered]
                        else:
                            all_dataframes[key].append(filtered)

        for table_name, df_list in all_dataframes.items():
            full_df = pd.concat(df_list, ignore_index=True)
            output_path = os.path.join(OUTPUT_FOLDER, f"{table_name}.csv")
            full_df.to_csv(output_path, index=False)

        st.success("All files processed and saved in:")
        st.code(OUTPUT_FOLDER)
else:
    st.info("Please enter a valid Data Date to continue.")
