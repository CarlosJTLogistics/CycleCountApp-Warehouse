import os
import csv
from typing import List, Dict

DATA_DIR = os.path.join(os.getcwd(), "data")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.csv")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp","user","location","sku","lot","expected_qty","counted_qty","issue_type","note"])

def append_submission(row: Dict[str,str]):
    ensure_data_dir()
    with open(SUBMISSIONS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp","user","location","sku","lot","expected_qty","counted_qty","issue_type","note"])
        writer.writerow(row)

def read_submissions() -> List[Dict[str,str]]:
    ensure_data_dir()
    with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)