import os, json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

DATA_DIR = os.path.join(os.getcwd(), "data")
ASSIGN_FILE = os.path.join(DATA_DIR, "assignments.json")

ASSIGNMENTS: Dict[str, Dict] = {}  # key: assignment_id
LOCK_MINUTES = 20

def _ensure():
    os.makedirs(DATA_DIR, exist_ok=True)

def save_all():
    _ensure()
    serializable = {}
    for k,v in ASSIGNMENTS.items():
        vv = v.copy()
        for dtk in ["created_at", "locked_until"]:
            if dtk in vv and isinstance(vv[dtk], datetime):
                vv[dtk] = vv[dtk].isoformat()
        serializable[k] = vv
    with open(ASSIGN_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

def load_all():
    global ASSIGNMENTS
    _ensure()
    if not os.path.exists(ASSIGN_FILE):
        return
    try:
        with open(ASSIGN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k,v in data.items():
            if "created_at" in v and isinstance(v["created_at"], str):
                v["created_at"] = datetime.fromisoformat(v["created_at"])
            if "locked_until" in v and isinstance(v["locked_until"], str):
                v["locked_until"] = datetime.fromisoformat(v["locked_until"])
        ASSIGNMENTS = data
    except Exception:
        ASSIGNMENTS = {}

def create_assignment(user: str, pallet_id: str, location: str, expected_qty: int) -> str:
    assignment_id = f"{user}-{pallet_id}-{int(datetime.utcnow().timestamp())}"
    ASSIGNMENTS[assignment_id] = {
        "user": user,
        "pallet_id": pallet_id,
        "location": location,
        "expected_qty": expected_qty,
        "created_at": datetime.utcnow(),
        "locked_until": datetime.utcnow() + timedelta(minutes=LOCK_MINUTES),
        "status": "assigned",
        "sku": "",
        "lot": ""
    }
    save_all()
    return assignment_id

def get_user_assignment_ids(user: str) -> List[str]:
    return [k for k,v in ASSIGNMENTS.items() if v.get("user")==user and v.get("status")=="assigned"]

def get(aid: str) -> Optional[Dict]:
    return ASSIGNMENTS.get(aid)

def get_user_assignments(user: str) -> List[Tuple[str, Dict]]:
    return [(k,v) for k,v in ASSIGNMENTS.items() if v.get("user")==user and v.get("status")=="assigned"]

def is_locked(assignment_id: str) -> bool:
    a = ASSIGNMENTS.get(assignment_id)
    return bool(a and datetime.utcnow() < a["locked_until"])

def complete(aid: str):
    a = ASSIGNMENTS.get(aid)
    if a:
        a["status"] = "completed"
        save_all()

# Load persisted state
load_all()