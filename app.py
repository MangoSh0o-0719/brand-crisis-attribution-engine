import streamlit as st
import pandas as pd
from pathlib import Path
import streamlit.components.v1 as components

# -----------------------------
# 0) Basics
# -----------------------------
st.set_page_config(page_title="Shein Sentiment Dashboard", page_icon="👗", layout="wide")
st.title("🛍️ Shein Modern Slavery: Public Sentiment & Risk Dashboard")

# 直接定位到你 GitHub 仓库中的 app_data 文件夹
PROJECT_ROOT = Path(".").resolve()
APP_DATA_DIR = PROJECT_ROOT / "app_data"

# -----------------------------
# 1) Utilities
# -----------------------------
def list_assets(dir_path: Path):
    if not dir_path.exists():
        return [], []
    htmls = sorted([p.name for p in dir_path.glob("*.html")])
    csvs = sorted([p.name for p in dir_path.glob("*.csv")])
    return htmls, csvs

def load_html_chart(file_name: str, height: int = 750):
    path = APP_DATA_DIR / file_name
    if path.exists():
        html_data = path.read_text(encoding="utf-8", errors="ignore")
        # 注入 CSS 确保图表在不同屏幕上完美适应
        responsive_css = "<style>body { margin: 0 !important; padding: 0 !important; overflow: hidden !important; }</style>"
        if "<head>" in html_data:
            html_data = html_data.replace("<head>", f"<head>{responsive_css}")
        else:
            html_data = responsive_css + html_data
        components.html(html_data, height=height, scrolling=False)
    else:
        st.error(f"⚠️ 找不到图表文件: {file_name}")
        st.caption(f"请检查 GitHub 中 `app_data/` 目录下是否确切存在此文件，注意大小写必须完全一致。")

# -----------------------------
# 2) Sidebar Navigation
# -----------------------------
st.sidebar.header("🎯 Navigation")

htmls, csvs = list_assets(APP_DATA_DIR)
st.sidebar.subheader("📦 App Data Assets")
st.sidebar.caption(f"已加载 HTML: {len(htmls)} 个 | CSV: {len(csvs)} 个")

with st.sidebar.expander("查看已加载的文件列表"):
    st.write("**HTML 图表:**", htmls if htmls else "空")
    st.write("**CSV 数据:**", csvs if csvs else "空")

st.sidebar.markdown("---")

current_view = st.sidebar.radio(
    "👁️ Select View:",
    [
        "📊 1. Macro Sentiment & Stance",
        "☢️ 2. Crisis Attribution & Deep Dive",
    ]
)

# -----------------------------
# 3) Pages
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