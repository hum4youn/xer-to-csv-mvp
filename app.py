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

st.title("XER to CSV Batch Processor")

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

                    if not xer_tables:
                        st.warning(f"No tables found in {filename}. Skipping.")
                        continue

                    for table_name, df in xer_tables.items():
                        if table_name not in all_dataframes:
                            all_dataframes[table_name] = [df]
                        else:
                            all_dataframes[table_name].append(df)

            if not all_dataframes:
                st.warning("No data was processed. Please check your input files.")
            else:
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
