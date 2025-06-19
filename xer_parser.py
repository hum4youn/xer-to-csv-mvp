# FILE: xer_parser.py

import pandas as pd

# Extended list of common Primavera XER tables
EXPECTED_TABLES = [
    'PROJECT', 'TASK', 'WBS', 'TASKPRED', 'TASKRSRC', 'RSRC',
    'UDFVALUE', 'UDFTYPE', 'CALENDAR', 'TASKCODE', 'PROJCOST',
    'ACTVCODE', 'ACTVTYPE', 'TASKACTV', 'FLOCATION', 'STEP',
    'TASKSTEP', 'OBS', 'PROJWBS', 'TASKPROC', 'TASKNOTE',
    'NOTE', 'ISSUE', 'THRESHOLD', 'THRESHVAL', 'PROJISSU',
    'FRA', 'COST', 'ACTV2TASK', 'RISK', 'RISKISSU', 'RISKNOTE',
    'RCAT', 'RISKTYPE', 'PROJFXN', 'FXN', 'PROJOBS', 'PROJPCAT',
    'PCAT', 'PCATVAL', 'PROJWXS', 'WXS', 'WXSSTEP', 'RSRCROLE',
    'ROLE', 'PROJRCAT', 'RCATVAL', 'EXCHANGE', 'EXCHRATE'
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

            if line.startswith('
