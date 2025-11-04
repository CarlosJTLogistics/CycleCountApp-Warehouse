import os
import time
from datetime import datetime, timezone
from typing import Dict

import streamlit as st
import pandas as pd
import pytz

# ---- App Metadata ----
APP_NAME = "CycleCountApp V2 — Warehouse"
APP_ICON = "📦"
DEFAULT_TZ = os.getenv("CC_TZ", "America/Chicago")

# Fixed assignee list (keep exactly as specified)
ASSIGN_NAME_OPTIONS = [
    "Aldo", "Alex", "Carlos", "Clayton", "Cody", "Enrique", "Eric",
    "James", "Jake", "Johntai", "Karen", "Kevin", "Luis", "Nyahok",
    "Stephanie", "Tyteanna"
]

FEATURE_FLAGS = {
    "sound_default_on": True,
    "vibration_default_on": True,
}

# ---- Error Guard ----
def _friendly_error(e: Exception):
    st.error("Something went wrong, but the app is still running safely.")
    with st.expander("Show diagnostics (copyable)"):
        st.code(f"{type(e).__name__}: {e}", language="text")

def guard_render(fn):
    def _wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            _friendly_error(e)
    return _wrapped

# ---- i18n ----
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
        "ready": "Ready",
        "footer": "Built for speed, safety, and clarity on the warehouse floor.",
        # Step 3 labels
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
        "download_csv": "Download Submissions CSV",
        "filter_by_user": "Filter by user",
        "filter_by_issue": "Filter by issue type",
        # Step 4 labels
        "inv_upload_map": "Inventory Upload & Mapping",
        "sheet": "Sheet",
        "header_row": "Header row (0-based)",
        "map_location": "Location column",
        "map_pallet": "Pallet ID column (optional)",
        "map_sku": "SKU column (optional)",
        "map_lot": "LOT column (optional)",
        "map_expected": "Expected QTY column (required)",
        "save_mapping": "Save Mapping",
        "mapping_saved": "Mapping saved.",
        "discrepancies": "Discrepancies",
        "non_match": "Non-Match Submissions",
        "bulk_discrepancies": "Bulk Discrepancies (per-pallet only)",
        # Step 5 labels
        "header_title": "Warehouse Cycle Count",
        "header_sub": "Fast • Accurate • Mobile-friendly",
        "complete": "Complete",
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
        "ready": "Listo",
        "footer": "Hecho para velocidad, seguridad y claridad en el almacén.",
        # Step 3 labels
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
        "download_csv": "Descargar CSV de Envíos",
        "filter_by_user": "Filtrar por usuario",
        "filter_by_issue": "Filtrar por tipo de incidencia",
        # Step 4 labels
        "inv_upload_map": "Carga y Mapeo de Inventario",
        "sheet": "Hoja",
        "header_row": "Fila de encabezado (índice 0)",
        "map_location": "Columna de Ubicación",
        "map_pallet": "Columna de ID de Tarima (opcional)",
        "map_sku": "Columna de SKU (opcional)",
        "map_lot": "Columna de LOTE (opcional)",
        "map_expected": "Columna de Cantidad Esperada (requerida)",
        "save_mapping": "Guardar Mapeo",
        "mapping_saved": "Mapeo guardado.",
        "discrepancies": "Discrepancias",
        "non_match": "Envíos No Coincidentes",
        "bulk_discrepancies": "Discrepancias de Bulk (por tarima)",
        # Step 5 labels
        "header_title": "Conteo Cíclico de Almacén",
        "header_sub": "Rápido • Preciso • Móvil",
        "complete": "Completar",
    },
}

def _init_lang() -> str:
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    return st.session_state["lang"]

def t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# ---- Session init ----
def init_state():
    ss = st.session_state
    ss.setdefault("splash_done", False)
    ss.setdefault("sound_on", FEATURE_FLAGS["sound_default_on"])
    ss.setdefault("vibration_on", FEATURE_FLAGS["vibration_default_on"])
    ss.setdefault("tz_name", DEFAULT_TZ)
    ss.setdefault("assign_lock_minutes", 20)
    ss.setdefault("inventory_loaded", False)
    ss.setdefault("mapping", {})
    ss.setdefault("map_sheet", None)
    ss.setdefault("map_header", 0)

def local_now(tz_name: str) -> datetime:
    try:
        tz = pytz.timezone(tz_name)
        return datetime.now(tz)
    except Exception:
        return datetime.now(timezone.utc)

# ---- UI helpers ----
def mobile_touch_css():
    st.markdown("""
    <style>
      .stButton>button { padding: 0.8rem 1.2rem; font-size: 1rem; }
      .stTextInput>div>div>input, .stNumberInput input { font-size: 1rem; }
      .stSelectbox div[data-baseweb='select'] { font-size: 1rem; }
      .block-container { padding-top: 1.0rem; }
      h1, h2, h3 { letter-spacing: 0.2px; }
      /* Header bar */
      .warehouse-header {
        background: linear-gradient(90deg, #F57C00, #ff9c3a);
        color: #111; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;
      }
      .warehouse-sub {
        color: #333; font-size: 0.9rem; margin-top: -6px; margin-bottom: 8px;
      }
      /* Card accent */
      .stMarkdown div, .stAlert { border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

def _header_bar():
    st.markdown(f"""
    <div class="warehouse-header">🏭 <b>{t('header_title')}</b></div>
    <div class="warehouse-sub">{t('header_sub')}</div>
    """, unsafe_allow_html=True)

@guard_render
def splash():
    if not st.session_state.get("splash_done"):
        st.title(t("welcome_title"))
        st.caption(t("welcome_sub"))
        with st.spinner(t("welcome_sub")):
            time.sleep(1.1)
        if st.button(t("continue"), type="primary"):
            st.session_state["splash_done"] = True
            st.rerun()
        st.stop()

def _local_timestamp_str():
    tzname = st.session_state.get("tz_name", DEFAULT_TZ)
    return local_now(tzname).strftime("%Y-%m-%d %I:%M:%S %p")

def _feedback_success():
    if not (st.session_state.get("sound_on") or st.session_state.get("vibration_on")):
        return
    import streamlit.components.v1 as components
    do_sound = "true" if st.session_state.get("sound_on") else "false"
    do_vibe  = "true" if st.session_state.get("vibration_on") else "false"
    components.html(f"""
    <audio id="beep" preload="auto">
      data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABYAAAABAA==
    </audio>
    <script>
      try {{
        if ({do_sound}) document.getElementById('beep').play().catch(()=>{});
        if ({do_vibe} && navigator.vibrate) navigator.vibrate([60,40,60]);
      }} catch (e) {{}}
    </script>
    """, height=0)

# ---- Data modules ----
import utils.storage as storage
import utils.assignments as A
import utils.mapping as M
storage.ensure_data_dir()

# ---- Sidebar (with Inventory Upload & Mapping) ----
def sidebar():
    with st.sidebar:
        st.selectbox(t("language"), options=["en", "es"], index=0 if _init_lang()=="en" else 1, key="lang")
        st.divider()
        st.toggle(t("sound"), key="sound_on")
        st.toggle(t("vibration"), key="vibration_on")
        st.selectbox(t("tz"), options=[st.session_state["tz_name"], "America/Chicago", "UTC"], key="tz_name")
        st.caption(f"{t('diag')}: {local_now(st.session_state['tz_name']).strftime('%Y-%m-%d %I:%M %p')}")
        st.divider()

        with st.expander(t("inv_upload_map"), expanded=False):
            uploaded = st.file_uploader("XLSX", type=["xlsx"], key="inv_upl_xlsx")
            if uploaded is not None:
                try:
                    M.save_inventory_bytes(uploaded.getvalue())
                    st.success("Inventory file saved.")
                    st.session_state["mapping"] = {}
                    st.session_state["map_sheet"] = None
                    st.session_state["map_header"] = 0
                except Exception as e:
                    _friendly_error(e)

            sheets = M.list_sheets()
            if sheets:
                st.session_state["map_sheet"] = st.selectbox(t("sheet"), options=sheets, index=0)
                st.session_state["map_header"] = st.number_input(t("header_row"), min_value=0, max_value=20, step=1, value=int(st.session_state.get("map_header",0)))
                df_preview = M.load_inventory_df(sheet_name=st.session_state["map_sheet"], header_row=st.session_state["map_header"])
                if not df_preview.empty:
                    cols = list(df_preview.columns)
                    location_col = st.selectbox(t("map_location"), options=[""] + cols, index=0)
                    pallet_col   = st.selectbox(t("map_pallet"), options=[""] + cols, index=0)
                    sku_col      = st.selectbox(t("map_sku"), options=[""] + cols, index=0)
                    lot_col      = st.selectbox(t("map_lot"), options=[""] + cols, index=0)
                    expected_col = st.selectbox(t("map_expected"), options=cols, index=0)

                    if st.button(t("save_mapping")):
                        try:
                            mapping = {
                                "sheet_name": st.session_state["map_sheet"],
                                "header_row": int(st.session_state["map_header"]),
                                "location_col": location_col or None,
                                "pallet_col": pallet_col or None,
                                "sku_col": sku_col or None,
                                "lot_col": lot_col or None,
                                "expected_col": expected_col,
                            }
                            M.save_mapping(mapping)
                            st.session_state["mapping"] = mapping
                            st.session_state["inventory_loaded"] = True
                            st.success(t("mapping_saved"))
                            st.rerun()
                        except Exception as e:
                            _friendly_error(e)
                else:
                    st.info("Upload a valid sheet to preview.")

# ---- Issue Type options ----
ISSUE_TYPE_OPTIONS = ["Match", "Over", "Short", "Misplaced", "Damaged", "Other"]

def _fmt_lock_remaining(a: dict) -> str:
    try:
        now = datetime.utcnow()
        rem = (a.get("locked_until") - now).total_seconds()
        if rem <= 0: return "unlocked"
        mins = int(rem // 60); secs = int(rem % 60)
        return f"{mins:02d}:{secs:02d} remaining"
    except Exception:
        return "locked"

# ---- Tabs ----
@guard_render
def tab_dashboard():
    st.subheader(t("tab_dashboard"))
    try:
        rows = storage.read_submissions()
        df = pd.DataFrame(rows)
        if df.empty:
            st.info("No submissions yet.")
            return

        # numeric coercion
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

        st.dataframe(df, use_container_width=True, height=300)

        # Discrepancies (hide MISSING)
        st.markdown("### " + t("discrepancies"))
        disc = df.copy()
        if "issue_type" in disc.columns:
            disc = disc[(disc["issue_type"].fillna("") != "Match") & (disc["issue_type"].fillna("") != "MISSING")]
        if disc.empty:
            st.caption("No discrepancies yet.")
        else:
            st.markdown("#### " + t("non_match"))
            st.dataframe(disc, use_container_width=True, height=200)

        # Bulk Discrepancies (per-pallet only) — using Actual Pallet, excluding TUN racks
        st.markdown("#### " + t("bulk_discrepancies"))
        if not disc.empty:
            bulk = disc[~disc["location"].fillna("").str.upper().str.startswith("TUN")]
            if "actual_pallet" in bulk.columns:
                try:
                    gb = bulk.groupby(["location","actual_pallet","sku","lot"], dropna=False, as_index=False).size()
                    for _, row in gb.iterrows():
                        loc = str(row.get("location",""))
                        pal = str(row.get("actual_pallet",""))
                        sku = str(row.get("sku",""))
                        lot = str(row.get("lot",""))
                        with st.expander(f"📦 {pal} @ {loc}  —  SKU {sku}  LOT {lot}"):
                            # show all lines that match this group
                            match_mask = (bulk["location"].astype(str)==loc) & (bulk["actual_pallet"].astype(str)==pal) & \
                                         (bulk["sku"].astype(str)==sku) & (bulk["lot"].astype(str)==lot)
                            st.dataframe(bulk[match_mask], use_container_width=True, height=160)
                except Exception as e:
                    _friendly_error(e)
            else:
                st.caption("No 'Actual Pallet' in data yet. Submit new entries to populate.")
        else:
            st.caption("No bulk discrepancies yet.")

        # Download CSV
        try:
            with open(storage.SUBMISSIONS_FILE, "rb") as f:
                st.download_button(label=t("download_csv"), data=f, file_name="submissions.csv", mime="text/csv")
        except Exception:
            st.warning("CSV not available yet.")
    except Exception as e:
        _friendly_error(e)

@guard_render
def tab_assignments():
    st.subheader(t("tab_assign"))

    # Assigner form
    with st.expander(t("assign_form_title"), expanded=True):
        c1, c2 = st.columns([1,1])
        with c1:
            assignee = st.selectbox(t("assignee"), ASSIGN_NAME_OPTIONS, index=0, key="assign_name")
            pallet_id = st.text_input(t("pallet_id"), key="assign_pallet")
        with c2:
            location = st.text_input(t("location"), key="assign_location")

            # Auto-fill Expected QTY from mapping if available
            autofill = None
            try:
                mapping = M.load_mapping()
                if mapping and M.has_inventory():
                    df_inv = M.load_inventory_df(sheet_name=mapping.get("sheet_name"), header_row=int(mapping.get("header_row",0)))
                    lookup = {
                        "pallet_col": pallet_id,
                        "location_col": location,
                        "sku_col": "",
                        "lot_col": "",
                    }
                    from utils.mapping import get_expected_qty
                    autofill = get_expected_qty(df_inv, mapping, lookup)
                    if autofill is not None and (st.session_state.get("assign_expected") in (None, 0, "")):
                        st.session_state["assign_expected"] = int(autofill)
            except Exception:
                pass

            st.number_input(t("expected_qty"), min_value=0, step=1, key="assign_expected")
        create = st.button(t("create"), type="primary")

        if create:
            try:
                if not assignee or not pallet_id or not location:
                    st.warning("Assignee, Pallet ID, and Location are required.")
                else:
                    expected = int(st.session_state.get("assign_expected") or 0)
                    aid = A.create_assignment(assignee, pallet_id.strip(), location.strip(), expected)
                    st.success(f"Assignment created: {aid}")
            except Exception as e:
                _friendly_error(e)

    # Assigned list
    st.markdown("### " + t("assigned_list"))
    try:
        all_assigned = list(A.ASSIGNMENTS.values())
        if not all_assigned:
            st.info(t("no_assignments"))
        else:
            for a in all_assigned:
                if a.get("status") != "assigned": continue
                cols = st.columns([2,2,2,1,1])
                cols[0].write(f"**{a['user']}**")
                cols[1].write(f"{t('pallet_id')}: {a['pallet_id']}")
                cols[2].write(f"{t('location')}: {a['location']}")
                cols[3].write(f"{t('expected_qty')}: {a['expected_qty']}")
                cols[4].write(f"{t('lock_status')}: {_fmt_lock_remaining(a)}")
    except Exception as e:
        _friendly_error(e)

    if not st.session_state.get("inventory_loaded"):
        st.caption("ℹ Tip: Upload inventory (sidebar) and save column mapping to enable auto Expected QTY.")

@guard_render
def tab_my_assignments():
    st.subheader(t("tab_my_assign"))

    user = st.selectbox(t("your_name"), ASSIGN_NAME_OPTIONS, index=0, key="my_name")
    pairs = A.get_user_assignments(user)  # list of (aid, dict)
    if not pairs:
        st.info(t("no_assignments"))
        return

    labels = [f"{a['pallet_id']} @ {a['location']}" for _, a in pairs]
    idx = st.selectbox(t("select_assignment"), options=list(range(len(labels))), format_func=lambda i: labels[i], key="my_assign_idx")
    aid, a = pairs[idx]

    st.markdown("### " + t("perform_count"))
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
        issue_type = st.selectbox(t("issue_type"), ["Match","Over","Short","Misplaced","Damaged","Other"], index=0, key="issue_type_sel")

    r3 = st.columns([1,2])
    with r3[0]:
        counted_qty = st.number_input(t("counted_qty"), min_value=0, step=1, value=int(a.get("expected_qty") or 0))
    with r3[1]:
        note = st.text_input(t("note"), value="")

    if st.button(t("submit"), type="primary"):
        try:
            row = {
                "timestamp": _local_timestamp_str(),
                "user": user,
                "location": a.get("location",""),
                "sku": a.get("sku",""),
                "lot": lot_actual,
                "expected_qty": str(a.get("expected_qty","")),
                "counted_qty": str(counted_qty),
                "issue_type": issue_type,
                "actual_pallet": actual_pallet,
                "note": note,
            }
            storage.append_submission(row)
            # Mark assignment completed
            A.complete(aid)
            _feedback_success()
            st.success(t("ready"))
            st.session_state["issue_type_sel"] = "Match"
            st.session_state["my_assign_idx"] = 0
            st.rerun()
        except Exception as e:
            _friendly_error(e)

@guard_render
def tab_settings():
    st.subheader(t("tab_settings"))
    st.write("• Sound:", "ON" if st.session_state.get("sound_on") else "OFF")
    st.write("• Vibration:", "ON" if st.session_state.get("vibration_on") else "OFF")
    st.write("• Timezone:", st.session_state.get("tz_name"))
    st.caption(t("footer"))

def main():
    st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="wide")
    init_state()
    mobile_touch_css()
    splash()
    _header_bar()  # visible warehouse theme header
    sidebar()
    tabs = st.tabs([t("tab_dashboard"), t("tab_assign"), t("tab_my_assign"), t("tab_settings")])
    with tabs[0]: tab_dashboard()
    with tabs[1]: tab_assignments()
    with tabs[2]: tab_my_assignments()
    with tabs[3]: tab_settings()

if __name__ == "__main__":
    main()