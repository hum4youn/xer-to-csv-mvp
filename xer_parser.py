# FILE: xer_parser.py

import pandas as pd
import os

# Define the list of tables expected from a typical XER file
EXPECTED_TABLES = [
    'PROJECT', 'TASK', 'WBS', 'TASKPRED', 'TASKRSRC', 'RSRC',
    'UDFVALUE', 'UDFTYPE', 'CALENDAR', 'TASKCODE', 'PROJCOST',
    'ACTVCODE', 'ACTVTYPE', 'TASKACTV', 'FLOCATION', 'STEP',
    'TASKSTEP', 'OBS', 'PROJWBS', 'TASKPROC'
]

def parse_xer_file(filepath):
    tables = {}
    current_table = None
    data = []

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue

            # Start of a new table
            if line.startswith('%T'):
                current_table = line[2:].strip()
                data = []
            
            # Column headers
            elif line.startswith('%F') and current_table:
                headers = line[2:].split('\t')
            
            # Data rows
            elif not line.startswith('%') and current_table:
                data.append(line.split('\t'))

            # End of table
            elif line.startswith('%E') and current_table:
                if current_table in EXPECTED_TABLES:
                    try:
                        df = pd.DataFrame(data, columns=headers)
                        tables[current_table] = df
                    except Exception as e:
                        print(f"Error parsing table {current_table}: {e}")
                current_table = None

    return tables
