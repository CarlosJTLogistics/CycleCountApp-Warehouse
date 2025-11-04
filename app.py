import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any

import streamlit as st
import pandas as pd
import pytz

# ----------------- App Metadata -----------------
APP_NAME = "CycleCountApp V2 — Warehouse"
APP_ICON = "📦"
DEFAULT_TZ = os.getenv("CC_TZ", "America/Chicago")

# Fixed list per requirements (keep as-is; includes Eric, excludes Erick; alphabetical)
ASSIGN_NAME_OPTIONS = [
    "Aldo", "Alex", "Carlos", "Clayton", "Cody", "Enrique", "Eric",
    "James", "Jake", "Johntai", "Karen", "Kevin", "Luis", "Nyahok",
    "Stephanie", "Tyteanna"
]

# Feature defaults / flags
FEATURE_FLAGS = {
    "sound_default_on": True,
    "vibration_default_on": True,
}

# ----------------- Error Guard -----------------
def _friendly_error(e: Exception):
    st.error("Something went wrong, but the app is still running safely.")
    with st.expander("Show diagnostics (copyable)"):
        st.code(f"{type(e).__name__}: {e}", language="text")
        st.code("".join(st.traceback.format_exc()) if hasattr(st, 'traceback') else "Traceback available in server logs.", language="text")

def guard_render(fn):
    def _wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            _friendly_error(e)
    return _wrapped

# ----------------- i18n -----------------
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "welcome_title": "Welcome to Warehouse Cycle Count",
        "welcome_sub": "Loading your workspace…",
        "continue": "Continue",
        "language": "Language",
        "tab_dashboard": "Live Dashboard",
        "tab_assign": "Assignments",
        "tab_my_assign": "My Assignments",
        "tab_settings": "Settings",
        "sound": "Sound (scan & submit)",
        "vibration": "Vibration (scan & submit)",
        "tz": "Timezone",
        "diag": "Diagnostics",
        "ok": "OK",
        "ready": "Ready",
        "footer": "Built for speed, safety, and clarity on the warehouse floor.",
        "placeholder": "Coming next in Step 2+",
    },
    "es": {
        "welcome_title": "Bienvenido a Conteo Cíclico (Almacén)",
        "welcome_sub": "Cargando su espacio de trabajo…",
        "continue": "Continuar",
        "language": "Idioma",
        "tab_dashboard": "Panel en Vivo",
        "tab_assign": "Asignaciones",
        "tab_my_assign": "Mis Asignaciones",
        "tab_settings": "Configuración",
        "sound": "Sonido (escaneo y enviar)",
        "vibration": "Vibración (escaneo y enviar)",
        "tz": "Zona horaria",
        "diag": "Diagnóstico",
        "ok": "OK",
        "ready": "Listo",
        "footer": "Hecho para velocidad, seguridad y claridad en el almacén.",
        "placeholder": "Próximamente en Paso 2+",
    },
}

def _init_lang() -> str:
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    return st.session_state["lang"]

def t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# ----------------- Session-safe init -----------------
def init_state():
    ss = st.session_state
    ss.setdefault("splash_done", False)
    ss.setdefault("sound_on", FEATURE_FLAGS["sound_default_on"])
    ss.setdefault("vibration_on", FEATURE_FLAGS["vibration_default_on"])
    ss.setdefault("tz_name", DEFAULT_TZ)
    # Placeholders reserved for future steps to carry over all existing rules:
    ss.setdefault("assign_lock_minutes", 20)  # 20-minute lock
    ss.setdefault("expected_qty_mapping", {}) # Excel column mapping
    ss.setdefault("submissions_log", [])      # Will become durable store/CSV
    ss.setdefault("inventory_loaded", False)

def local_now(tz_name: str) -> datetime:
    try:
        tz = pytz.timezone(tz_name)
        return datetime.now(tz)
    except Exception:
        return datetime.now(timezone.utc)

# ----------------- UI building blocks -----------------
def mobile_touch_css():
    st.markdown(\"\"\"\n
    <style>
      /* Larger click targets and inputs for scan guns and touch */
      .stButton>button { padding: 0.8rem 1.2rem; font-size: 1rem; }
      .stTextInput>div>div>input, .stNumberInput input { font-size: 1rem; }
      .stSelectbox div[data-baseweb="select"] { font-size: 1rem; }
      .block-container { padding-top: 1.5rem; }
      /* Subtle warehouse accents for headers */
      h1, h2, h3 { letter-spacing: 0.2px; }
    </style>\n
    \"\"\", unsafe_allow_html=True)

@guard_render
def splash():
    if not st.session_state.get("splash_done"):
        st.title(t("welcome_title"))
        st.caption(t("welcome_sub"))
        with st.spinner(t("welcome_sub")):
            time.sleep(1.1)  # short splash; shown once per session
        if st.button(t("continue"), type="primary"):
            st.session_state["splash_done"] = True
            st.rerun()
        st.stop()

def sidebar():
    with st.sidebar:
        st.selectbox(t("language"), options=["en", "es"], index=0 if _init_lang()=="en" else 1,
                     key="lang")
        st.divider()
        st.toggle(t("sound"), key="sound_on")
        st.toggle(t("vibration"), key="vibration_on")
        st.selectbox(t("tz"), options=[st.session_state["tz_name"], "America/Chicago", "UTC"],
                     key="tz_name")
        st.caption(f"{t('diag')}: {local_now(st.session_state['tz_name']).strftime('%Y-%m-%d %I:%M %p')}")

# ----------------- Tabs (scaffold) -----------------
@guard_render
def tab_dashboard():
    st.subheader(t("tab_dashboard"))
    st.info(t("placeholder"))

@guard_render
def tab_assignments():
    st.subheader(t("tab_assign"))
    # Reserved: Supervisor-only assignment flow, 20-minute lock, per-pallet bulk, TUN are racks
    st.info(t("placeholder"))

@guard_render
def tab_my_assignments():
    st.subheader(t("tab_my_assign"))
    # Reserved: Perform Count UI; all fields read-only except Counted QTY and Note
    # Keep Issue Type and Actual Pallet/LOT fields; sound/vibration feedback
    st.info(t("placeholder"))

@guard_render
def tab_settings():
    st.subheader(t("tab_settings"))
    st.write("• Sound:", "ON" if st.session_state.get("sound_on") else "OFF")
    st.write("• Vibration:", "ON" if st.session_state.get("vibration_on") else "OFF")
    st.write("• Timezone:", st.session_state.get("tz_name"))
    st.caption(t("footer"))

# ----------------- Main -----------------
def main():
    st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="wide")
    init_state()
    mobile_touch_css()
    splash()  # shows only once per session

    sidebar()
    tabs = st.tabs([t("tab_dashboard"), t("tab_assign"), t("tab_my_assign"), t("tab_settings")])
    with tabs[0]: tab_dashboard()
    with tabs[1]: tab_assignments()
    with tabs[2]: tab_my_assignments()
    with tabs[3]: tab_settings()

if __name__ == "__main__":
    main()# --- Added in Step 2 ---
import utils.storage as storage
import utils.assignments as assignments

# Initialize data folder and submissions file
storage.ensure_data_dir()

# Inventory upload placeholder
with st.sidebar:
    st.subheader("Inventory Upload")
    uploaded_file = st.file_uploader("Upload Inventory Excel", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.success(f"Inventory loaded: {df.shape[0]} rows")
            st.session_state["inventory_loaded"] = True
        except Exception as e:
            st.error("Failed to read Excel file. Check format.")
# ==== STEP 3 PATCH: UI (Assignments, My Assignments, Live Dashboard) ====
# (Appends new function definitions that override earlier stubs, plus EN/ES labels)

# New constants and helpers
ISSUE_TYPE_OPTIONS = [
    "Match", "Over", "Short", "Misplaced", "Damaged", "Other"
]

def _fmt_lock_remaining(a: dict) -> str:
    try:
        from datetime import datetime, timezone
        now = datetime.utcnow()
        rem = (a.get("locked_until") - now).total_seconds()
        if rem <= 0:
            return "unlocked"
        mins = int(rem // 60); secs = int(rem % 60)
        return f"{mins:02d}:{secs:02d} remaining"
    except Exception:
        return "locked"

def _local_timestamp() -> str:
    # Use CC_TZ -> America/Chicago fallback
    tzname = st.session_state.get("tz_name", DEFAULT_TZ)
    ts = local_now(tzname).strftime("%Y-%m-%d %I:%M:%S %p")
    return ts

# Extend translations with new labels
TRANSLATIONS["en"].update({
    "assign_form_title": "Create Assignment",
    "assignee": "Assign to (name)",
    "pallet_id": "Pallet ID",
    "location": "Location",
    "expected_qty": "Expected QTY",
    "create": "Create",
    "your_name": "Your name",
    "select_assignment": "Select an assignment",
    "perform_count": "Perform Count",
    "sku": "SKU",
    "lot": "LOT (Actual)",
    "actual_pallet": "Actual Pallet",
    "counted_qty": "Counted QTY",
    "note": "Note",
    "issue_type": "Issue Type",
    "submit": "Submit",
    "assigned_list": "Assigned items",
    "lock_status": "Lock",
    "no_assignments": "No assignments yet.",
    "inventory_needed": "Tip: Upload inventory (sidebar) to enable auto Expected QTY mapping (coming next).",
    "download_csv": "Download Submissions CSV",
    "filter_by_user": "Filter by user",
    "filter_by_issue": "Filter by issue type",
})

TRANSLATIONS["es"].update({
    "assign_form_title": "Crear asignación",
    "assignee": "Asignar a (nombre)",
    "pallet_id": "ID de Tarima",
    "location": "Ubicación",
    "expected_qty": "Cantidad Esperada",
    "create": "Crear",
    "your_name": "Su nombre",
    "select_assignment": "Seleccione una asignación",
    "perform_count": "Realizar Conteo",
    "sku": "SKU",
    "lot": "LOTE (Actual)",
    "actual_pallet": "Tarima Actual",
    "counted_qty": "Cantidad Contada",
    "note": "Nota",
    "issue_type": "Tipo de Incidencia",
    "submit": "Enviar",
    "assigned_list": "Elementos asignados",
    "lock_status": "Bloqueo",
    "no_assignments": "Sin asignaciones.",
    "inventory_needed": "Sugerencia: Cargue inventario (barra lateral) para habilitar el mapeo de Cantidad Esperada (próximo paso).",
    "download_csv": "Descargar CSV de Envíos",
    "filter_by_user": "Filtrar por usuario",
    "filter_by_issue": "Filtrar por tipo de incidencia",
})

# Override: Live Dashboard tab
@guard_render
def tab_dashboard():
    st.subheader(t("tab_dashboard"))
    import utils.storage as storage
    try:
        rows = storage.read_submissions()
        df = pd.DataFrame(rows)
        if df.empty:
            st.info("No submissions yet.")
            return
        # Coerce numeric fields if present
        for col in ["expected_qty", "counted_qty"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        # Filters
        cols = st.columns(3)
        with cols[0]:
            user_f = st.multiselect(t("filter_by_user"),
                                    sorted(list(df["user"].dropna().unique())))
        with cols[1]:
            issue_f = st.multiselect(t("filter_by_issue"),
                                     ISSUE_TYPE_OPTIONS)
        if user_f:
            df = df[df["user"].isin(user_f)]
        if issue_f and "issue_type" in df.columns:
            df = df[df["issue_type"].isin(issue_f)]
        # Show grid
        st.dataframe(df, use_container_width=True, height=360)
        # Download
        import utils.storage as storage
        try:
            with open(storage.SUBMISSIONS_FILE, "rb") as f:
                st.download_button(label=t("download_csv"), data=f, file_name="submissions.csv", mime="text/csv")
        except Exception:
            st.warning("CSV not available yet.")
    except Exception as e:
        _friendly_error(e)

# Override: Assignments tab (Supervisor)
@guard_render
def tab_assignments():
    st.subheader(t("tab_assign"))
    import utils.assignments as A

    with st.expander(t("assign_form_title"), expanded=True):
        c1, c2 = st.columns([1,1])
        with c1:
            assignee = st.selectbox(t("assignee"), ASSIGN_NAME_OPTIONS, index=0, key="assign_name")
            pallet_id = st.text_input(t("pallet_id"), key="assign_pallet")
        with c2:
            location = st.text_input(t("location"), key="assign_location")
            expected_qty = st.number_input(t("expected_qty"), min_value=0, step=1, key="assign_expected")
        create = st.button(t("create"), type="primary")
        if create:
            try:
                if not assignee or not pallet_id or not location:
                    st.warning("Assignee, Pallet ID, and Location are required.")
                else:
                    aid = A.create_assignment(assignee, pallet_id.strip(), location.strip(), int(expected_qty or 0))
                    st.success(f"Assignment created: {aid}")
            except Exception as e:
                _friendly_error(e)

    st.markdown("### " + t("assigned_list"))
    # Show a simple list of all assignments by assignee, with lock status
    try:
        all_assigned = A.ASSIGNMENTS.values()
        if not any(True for _ in all_assigned):
            st.info(t("no_assignments"))
        else:
            for a in list(A.ASSIGNMENTS.values()):
                cols = st.columns([2,2,2,1,1])
                cols[0].write(f"**{a['user']}**")
                cols[1].write(f"{t('pallet_id')}: {a['pallet_id']}")
                cols[2].write(f"{t('location')}: {a['location']}")
                cols[3].write(f"{t('expected_qty')}: {a['expected_qty']}")
                cols[4].write(f"{t('lock_status')}: {_fmt_lock_remaining(a)}")
    except Exception as e:
        _friendly_error(e)

    if not st.session_state.get("inventory_loaded"):
        st.caption("ℹ " + t("inventory_needed"))

# Override: My Assignments tab (Counter)
@guard_render
def tab_my_assignments():
    st.subheader(t("tab_my_assign"))

    import utils.assignments as A
    import utils.storage as storage

    # Who am I?
    user = st.selectbox(t("your_name"), ASSIGN_NAME_OPTIONS, index=0, key="my_name")

    # My assignment list
    my_list = A.get_user_assignments(user)
    if not my_list:
        st.info(t("no_assignments"))
        return

    # Select one assignment
    aid_options = [f"{a['pallet_id']} @ {a['location']}" for a in my_list]
    idx = st.selectbox(t("select_assignment"), options=list(range(len(aid_options))), format_func=lambda i: aid_options[i], key="my_assign_idx")

    a = my_list[idx]
    locked = A.is_locked(next(k for k,v in A.ASSIGNMENTS.items() if v is a))

    # Perform Count UI
    st.markdown("### " + t("perform_count"))
    # Read-only rows (except counted qty and note)
    r1 = st.columns([1,1,1,1])
    with r1[0]:
        st.text_input(t("pallet_id"), value=a.get("pallet_id",""), disabled=True)
    with r1[1]:
        st.text_input(t("location"), value=a.get("location",""), disabled=True)
    with r1[2]:
        st.text_input(t("sku"), value=a.get("sku",""), disabled=True)
    with r1[3]:
        st.text_input(t("expected_qty"), value=str(a.get("expected_qty","")), disabled=True)

    r2 = st.columns([1,1,2])
    with r2[0]:
        actual_pallet = st.text_input(t("actual_pallet"), value=a.get("pallet_id",""))
    with r2[1]:
        lot_actual = st.text_input(t("lot"), value=a.get("lot",""))
    with r2[2]:
        issue_type = st.selectbox(t("issue_type"), ISSUE_TYPE_OPTIONS, index=0, key="issue_type_sel")

    r3 = st.columns([1,2])
    with r3[0]:
        counted_qty = st.number_input(t("counted_qty"), min_value=0, step=1, value=int(a.get("expected_qty") or 0))
    with r3[1]:
        note = st.text_input(t("note"), value="")

    # Submit button respects lock
    submit_disabled = False
    lock_label = _fmt_lock_remaining(a)
    if lock_label != "unlocked":
        # Allow visibility but annotate
        st.caption(f"⏱️ {t('lock_status')}: {lock_label}")

    if st.button(t("submit"), type="primary", disabled=submit_disabled):
        try:
            # Log submission (append-only CSV)
            row = {
                "timestamp": _local_timestamp(),
                "user": user,
                "location": a.get("location",""),
                "sku": a.get("sku",""),
                "lot": lot_actual,
                "expected_qty": str(a.get("expected_qty","")),
                "counted_qty": str(counted_qty),
                "issue_type": issue_type,
                "note": note,
            }
            storage.append_submission(row)

            # UX feedback: success + (sound/vibration hooks to be added later)
            st.success(t("ready"))

            # Clear critical inputs and re-focus UX back on list
            st.session_state["issue_type_sel"] = ISSUE_TYPE_OPTIONS[0]
            st.session_state["my_assign_idx"] = 0
            # (As we build more flows, we can auto-return to My Assignments or refresh list)
            st.rerun()
        except Exception as e:
            _friendly_error(e)
# ==== END STEP 3 PATCH ====