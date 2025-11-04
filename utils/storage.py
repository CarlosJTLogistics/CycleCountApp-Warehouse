import os
import csv
import tempfile
from typing import List, Dict

DATA_DIR = os.path.join(os.getcwd(), "data")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.csv")

REQUIRED_FIELDS = [
    "timestamp","user","location","sku","lot",
    "expected_qty","counted_qty","issue_type","actual_pallet","note"
]

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(REQUIRED_FIELDS)
    else:
        _migrate_columns_if_needed()

def _read_header(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            row = next(reader, None)
            return row or []
    except Exception:
        return []

def _migrate_columns_if_needed():
    """Ensure the CSV has REQUIRED_FIELDS. If missing columns, rewrite with new header and preserve data."""
    header = _read_header(SUBMISSIONS_FILE)
    if not header:
        # empty or corrupt -> rewrite header only
        with open(SUBMISSIONS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f); writer.writerow(REQUIRED_FIELDS)
        return

    if all(col in header for col in REQUIRED_FIELDS) and len(header) == len(REQUIRED_FIELDS):
        return  # already correct

    # Read all rows as dicts using existing header
    rows = []
    try:
        with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception:
        rows = []

    # Write temp with REQUIRED_FIELDS
    fd, tmp = tempfile.mkstemp(prefix="submissions_", suffix=".csv", dir=DATA_DIR)
    os.close(fd)
    try:
        with open(tmp, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=REQUIRED_FIELDS)
            writer.writeheader()
            for r in rows:
                out = {k: r.get(k, "") for k in REQUIRED_FIELDS}
                writer.writerow(out)
        # Atomic replace
        os.replace(tmp, SUBMISSIONS_FILE)
    finally:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except Exception: pass

def append_submission(row: Dict[str,str]):
    ensure_data_dir()
    # Guarantee all required fields are present
    out = {k: row.get(k, "") for k in REQUIRED_FIELDS}
    with open(SUBMISSIONS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_FIELDS)
        writer.writerow(out)

def read_submissions() -> List[Dict[str,str]]:
    ensure_data_dir()
    with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)