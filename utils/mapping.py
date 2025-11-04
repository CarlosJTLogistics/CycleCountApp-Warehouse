import os
import json
import pandas as pd
from typing import Dict, Optional

DATA_DIR = os.path.join(os.getcwd(), "data")
INV_FILE = os.path.join(DATA_DIR, "inventory.xlsx")
MAP_FILE = os.path.join(DATA_DIR, "mapping.json")

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def save_inventory_bytes(file_bytes: bytes) -> str:
    ensure_data_dir()
    with open(INV_FILE, "wb") as f:
        f.write(file_bytes)
    return INV_FILE

def has_inventory() -> bool:
    return os.path.exists(INV_FILE)

def list_sheets() -> list:
    if not has_inventory():
        return []
    try:
        xl = pd.ExcelFile(INV_FILE, engine="openpyxl")
        return xl.sheet_names
    except Exception:
        return []

def load_inventory_df(sheet_name: Optional[str] = None, header_row: int = 0) -> pd.DataFrame:
    if not has_inventory():
        return pd.DataFrame()
    try:
        return pd.read_excel(INV_FILE, engine="openpyxl", sheet_name=sheet_name, header=header_row)
    except Exception:
        return pd.DataFrame()

def save_mapping(mapping: Dict):
    ensure_data_dir()
    with open(MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

def load_mapping() -> Dict:
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _to_int(val):
    try:
        return int(val)
    except Exception:
        try:
            return int(float(val))
        except Exception:
            return None

def get_expected_qty(df: pd.DataFrame, mapping: Dict, lookup: Dict) -> Optional[int]:
    """
    mapping keys:
      - sheet_name, header_row
      - expected_col (required)
      - location_col, pallet_col, sku_col, lot_col (optional)
    lookup keys must correspond to *_col names above (values are the lookup values)
    Try strategies in order of specificity:
      (pallet+location) -> pallet -> location -> (sku+lot) -> sku
    """
    try:
        if df is None or df.empty or not mapping or not mapping.get("expected_col"):
            return None
        m = mapping
        def filt(d, fkey):
            col = m.get(fkey)
            val = lookup.get(fkey)
            if not col or col not in d.columns or val in (None, ""):
                return None
            return d[d[col].astype(str).str.strip() == str(val).strip()]

        strategies = [
            ["pallet_col","location_col"],
            ["pallet_col"],
            ["location_col"],
            ["sku_col","lot_col"],
            ["sku_col"]
        ]
        for fields in strategies:
            sub = df
            ok = True
            for f in fields:
                res = filt(sub, f)
                if res is None:
                    ok = False
                    break
                sub = res
            if ok and sub is not None and not sub.empty:
                val = sub[m["expected_col"]].iloc[0]
                return _to_int(val)
        return None
    except Exception:
        return None