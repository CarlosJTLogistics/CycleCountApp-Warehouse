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
