# FILE: app.py

import streamlit as st
import zipfile
import os
import pandas as pd
import shutil
import tempfile
from io import BytesIO
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

    st.subheader("Upload Files")
    zip_file = st.file_uploader("Upload a ZIP file of XERs (optional)", type="zip")
    xer_file = st.file_uploader("Upload a single XER file (optional)", type="xer")

    if zip_file or xer_file:
        with tempfile.TemporaryDirectory() as temp_dir:
            extracted_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extracted_dir, exist_ok=True)

            if zip_file:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(extracted_dir)

            if xer_file:
                xer_path = os.path.join(extracted_dir, xer_file.name)
                with open(xer_path, 'wb') as f:
                    f.write(xer_file.read())

            all_dataframes = {}

            for filename in os.listdir(extracted_dir):
                if filename.endswith(".xer"):
                    xer_path = os.path.join(extracted_dir, filename)
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

            # Write all output to a temporary folder for zipping
            output_temp_dir = os.path.join(temp_dir, "csv_outputs")
            os.makedirs(output_temp_dir, exist_ok=True)

            for table_name, df_list in all_dataframes.items():
                full_df = pd.concat(df_list, ignore_index=True)
                output_path = os.path.join(output_temp_dir, f"{table_name}.csv")
                full_df.to_csv(output_path, index=False)

            # Zip the CSV files
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_out:
                for csv_file in os.listdir(output_temp_dir):
                    full_path = os.path.join(output_temp_dir, csv_file)
                    zip_out.write(full_path, arcname=csv_file)

            zip_buffer.seek(0)
            st.success("Processing complete. Download your CSVs:")
            st.download_button("Download CSV ZIP", zip_buffer, file_name=f"XER_CSVs_{data_date_str}.zip")
else:
    st.info("Please enter a valid Data Date to continue.")
