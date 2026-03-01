import streamlit as st
import pandas as pd
import os
import glob
import shutil
from pathlib import Path
import streamlit.components.v1 as components

# -----------------------------
# 0) Basics
# -----------------------------
st.set_page_config(page_title="Shein Sentiment Dashboard", page_icon="👗", layout="wide")
st.title("🛍️ Shein Modern Slavery: Public Sentiment & Risk Dashboard")

PROJECT_ROOT = Path(".").resolve()
APP_DATA_DIR = PROJECT_ROOT / "app_data"
DATA_DIR = PROJECT_ROOT / "Data"

APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# 1) Utilities
# -----------------------------
def get_latest_dir(pattern: str) -> Path | None:
    cands = glob.glob(str(DATA_DIR / pattern))
    dirs = [Path(d) for d in cands if Path(d).is_dir()]
    if not dirs:
        return None
    return max(dirs, key=lambda p: p.stat().st_mtime)

def safe_copy(src: Path, dst_dir: Path):
    try:
        if src.is_file():
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(src), str(dst_dir))
    except Exception as e:
        st.warning(f"Copy failed: {src.name} ({e})")

def list_assets(dir_path: Path):
    htmls = sorted([p.name for p in dir_path.glob("*.html")])
    csvs = sorted([p.name for p in dir_path.glob("*.csv")])
    return htmls, csvs

def load_html_chart(file_name: str, height: int = 750):
    path = APP_DATA_DIR / file_name
    if path.exists():
        html_data = path.read_text(encoding="utf-8", errors="ignore")
        responsive_css = "<style>body { margin: 0 !important; padding: 0 !important; overflow: hidden !important; }</style>"
        if "<head>" in html_data:
            html_data = html_data.replace("<head>", f"<head>{responsive_css}")
        else:
            html_data = responsive_css + html_data
        components.html(html_data, height=height, scrolling=False)
    else:
        st.warning(f"Missing chart: {file_name} (expected at {path.as_posix()})")

def load_csv_data(file_name: str) -> pd.DataFrame:
    path = APP_DATA_DIR / file_name
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception as e:
            st.warning(f"Failed to read CSV: {file_name} ({e})")
    return pd.DataFrame()

# -----------------------------
# 2) Asset sync (optional)
#   - For Streamlit Cloud, you should commit demo artifacts into app_data/
#   - Sync is mainly for local dev when you have Data/ outputs.
# -----------------------------
@st.cache_resource(show_spinner="正在从 Data 目录同步最新资产...")
def sync_assets_to_app_data():
    print("🚀 Starting automated asset synchronization...")
    PROJECT_ROOT = "." 
    APP_DATA_DIR = os.path.join(PROJECT_ROOT, "app_data")
    DATA_DIR = os.path.join(PROJECT_ROOT, "Data")

    # 🌟 核心修复：云端防傻机制！(千万别漏了这段)
    if not os.path.exists(DATA_DIR):
        print("☁️ 检测到云端环境 (无 Data/ 文件夹)。保留现有 app_data/，跳过同步。")
        return "Cloud (06)", "Cloud (07)", "Cloud (08)"

    # ======= 以下是你在本地运行时的同步逻辑 =======
    if os.path.exists(APP_DATA_DIR):
        try:
            shutil.rmtree(APP_DATA_DIR)
        except Exception as e:
            print(f"Warning: Could not remove {APP_DATA_DIR}: {e}")
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    # (keep any committed demo assets)
    def copy_patterns(src_dir: Path, patterns: list[str]):
        for pattern in patterns:
            for fp in src_dir.glob(pattern):
                if fp.is_file():
                    safe_copy(fp, APP_DATA_DIR)

    latest_06 = get_latest_dir("data_06*")
    if latest_06:
        # allow nested html/csv
        for fp in latest_06.rglob("*.html"):
            safe_copy(fp, APP_DATA_DIR)
        for fp in latest_06.rglob("*.csv"):
            safe_copy(fp, APP_DATA_DIR)

    latest_07 = get_latest_dir("data_07*")
    if latest_07:
        for fp in latest_07.rglob("*.html"):
            safe_copy(fp, APP_DATA_DIR)
        for fp in latest_07.rglob("*.csv"):
            safe_copy(fp, APP_DATA_DIR)

    latest_08 = get_latest_dir("data_08*")
    if latest_08:
        # your 08 commonly saves figs/*.html + *.csv
        for fp in (latest_08 / "figs").glob("*.html"):
            safe_copy(fp, APP_DATA_DIR)
        for fp in latest_08.glob("*.csv"):
            safe_copy(fp, APP_DATA_DIR)

    return latest_06, latest_07, latest_08

# -----------------------------
# 3) Sidebar
# -----------------------------
st.sidebar.header("🎯 Navigation")

enable_sync = st.sidebar.toggle(
    "🔄 Sync from Data/ (local dev only)",
    value=False,
    help="On Streamlit Cloud, you typically commit demo outputs into app_data/ and keep Data/ out of git."
)

latest_06_dir, latest_07_dir, latest_08_dir = sync_assets_to_app_data(enable_sync)

if st.sidebar.button("🔁 Refresh (rerun)"):
    sync_assets_to_app_data.clear()
    st.rerun()

st.sidebar.markdown("---")

htmls, csvs = list_assets(APP_DATA_DIR)
st.sidebar.subheader("📦 app_data assets")
st.sidebar.caption(f"HTML: {len(htmls)} | CSV: {len(csvs)}")
with st.sidebar.expander("Show file list"):
    st.write("HTML:", htmls if htmls else "None")
    st.write("CSV:", csvs if csvs else "None")

st.sidebar.markdown("---")
if latest_06_dir:
    st.sidebar.success(f"📂 latest_06 mounted: `{latest_06_dir.name}`")
if latest_07_dir:
    st.sidebar.success(f"📂 latest_07 mounted: `{latest_07_dir.name}`")
if latest_08_dir:
    st.sidebar.success(f"📂 latest_08 mounted: `{latest_08_dir.name}`")

current_view = st.sidebar.radio(
    "👁️ Select View:",
    [
        "📊 1. Macro Sentiment & Stance",
        "☢️ 2. Crisis Attribution & Deep Dive",
    ]
)

# -----------------------------
# 4) Pages
# -----------------------------
if current_view == "📊 1. Macro Sentiment & Stance":
    st.header("Macro Sentiment Overview & Audience Stance")

    st.subheader("Group Risk Drivers (Stacked)")
    load_html_chart("01_group_risk_drivers_stacked.html", height=600)
    st.divider()

    st.subheader("Risk Score Distribution (Violin)")
    load_html_chart("02_risk_score_distribution_violin.html", height=650)
    st.divider()

    st.subheader("Primary Contrast Delta (95% CI)")
    load_html_chart("03_primary_contrast_delta_ci.html", height=650)
    st.divider()

    st.subheader("Risk Quadrant: Net Negative vs Amplification")
    load_html_chart("05_quadrant_netneg_vs_amplification.html", height=700)
    st.divider()

    st.subheader("Bootstrap Statistics & Contingency Tables")
    load_html_chart("04_bootstrap_tables_combined.html", height=1200)

elif current_view == "☢️ 2. Crisis Attribution & Deep Dive":
    st.header("Crisis Topic Modeling & Attribution")
    st.markdown(
        "This section is based on semantic clustering + C-TF-IDF, "
        "and a stance-aware priority score that fuses sentiment, amplification, and NLI dynamics."
    )

    st.subheader("Audience Stance Breakdown (NLI)")
    load_html_chart("06_nli_stance_distribution_stacked.html", height=520)
    st.divider()

    st.subheader("Topic Landscape: Net Negative × Amplification (Color = Lift)")
    load_html_chart("01_topic_bubble_netneg_x_amp.html", height=760)
    st.divider()

    st.subheader("Exclusive Risk (Lift)")
    load_html_chart("02_topic_lift_bar_primary.html", height=820)
    st.divider()

    st.subheader("Priority Ranking (Stance-Aware)")
    load_html_chart("03_priority_ranking_stance_aware.html", height=920)
    st.divider()

    st.subheader("Attribution Risk Matrix (Lift × Priority)")
    load_html_chart("04_attribution_risk_matrix.html", height=760)
