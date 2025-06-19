# FILE: xer_parser.py

import pandas as pd

EXPECTED_TABLES = [
    'PROJECT', 'TASK', 'WBS', 'TASKPRED', 'TASKRSRC', 'RSRC',
    'UDFVALUE', 'UDFTYPE', 'CALENDAR', 'TASKCODE', 'PROJCOST',
    'ACTVCODE', 'ACTVTYPE', 'TASKACTV', 'FLOCATION', 'STEP',
    'TASKSTEP', 'OBS', 'PROJWBS', 'TASKPROC', 'TASKNOTE'
]

def parse_xer_file(filepath):
    tables = {}
    current_table = None
    headers = []
    data = []

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith('%T'):
                current_table = line[2:].strip()
                headers = []
                data = []

            elif line.startswith('%F') and current_table:
                headers = line[2:].split('\t')

            elif not line.startswith('%') and current_table:
                data.append(line.split('\t'))

            elif line.startswith('%E') and current_table:
                if current_table in EXPECTED_TABLES and headers:
                    try:
                        df = pd.DataFrame(data, columns=headers)
                        tables[current_table] = df
                    except Exception as e:
                        print(f"Error parsing {current_table}: {e}")
                current_table = None
                headers = []
                data = []

    return tables
