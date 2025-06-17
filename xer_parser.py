import pandas as pd

def parse_xer(file_content: str):
    tables = {}
    lines = file_content.splitlines()
    current_table = None
    current_data = []

    for line in lines:
        line = line.strip()
        if line.startswith("%T"):
            if current_table and current_data:
                df = pd.DataFrame([row.split('\t') for row in current_data])
                tables[current_table] = df
            current_table = line.replace("%T", "").strip()
            current_data = []
        elif current_table:
            current_data.append(line)

    # Add last table
    if current_table and current_data:
        df = pd.DataFrame([row.split('\t') for row in current_data])
        tables[current_table] = df

    return tables
