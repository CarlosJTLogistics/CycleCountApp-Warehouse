from datetime import datetime, timedelta
from typing import Dict, List

ASSIGNMENTS: Dict[str, Dict] = {}  # key: assignment_id

LOCK_MINUTES = 20

def create_assignment(user: str, pallet_id: str, location: str, expected_qty: int) -> str:
    assignment_id = f"{user}-{pallet_id}-{int(datetime.utcnow().timestamp())}"
    ASSIGNMENTS[assignment_id] = {
        "user": user,
        "pallet_id": pallet_id,
        "location": location,
        "expected_qty": expected_qty,
        "created_at": datetime.utcnow(),
        "locked_until": datetime.utcnow() + timedelta(minutes=LOCK_MINUTES),
        "status": "assigned"
    }
    return assignment_id

def get_user_assignments(user: str) -> List[Dict]:
    return [a for a in ASSIGNMENTS.values() if a["user"] == user]

def is_locked(assignment_id: str) -> bool:
    a = ASSIGNMENTS.get(assignment_id)
    return a and datetime.utcnow() < a["locked_until"]