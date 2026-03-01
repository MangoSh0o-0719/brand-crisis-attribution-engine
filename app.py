import streamlit as st
import pandas as pd
import os
import glob
import shutil
import streamlit.components.v1 as components

# --- 1. 页面基本设置 ---
st.set_page_config(page_title="Shein Sentiment Dashboard", page_icon="👗", layout="wide")
st.title("🛍️ Shein Modern Slavery: Public Sentiment & Risk Dashboard")

# --- 2. 自动化资产同步 ---
@st.cache_resource(show_spinner="正在从 Data 目录同步最新资产...")
def sync_assets_to_app_data():
    print("🚀 Starting automated asset synchronization...")
    PROJECT_ROOT = "." 
    APP_DATA_DIR = os.path.join(PROJECT_ROOT, "app_data")
    DATA_DIR = os.path.join(PROJECT_ROOT, "Data")

    if os.path.exists(APP_DATA_DIR):
        try:
            shutil.rmtree(APP_DATA_DIR)
        except Exception as e:
            print(f"Warning: Could not remove {APP_DATA_DIR}: {e}")
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    
    def get_latest_dir(pattern: str) -> str:
        cands = glob.glob(os.path.join(DATA_DIR, pattern))
        dirs = [d for d in cands if os.path.isdir(d)]
        if not dirs:
            return None
        return max(dirs, key=os.path.getmtime)

    # 同步 06 (大盘图表)
    latest_06 = get_latest_dir("data_06*")
    if latest_06:
        for pattern in ["**/*.html", "**/*.csv"]:
            for file_path in glob.glob(os.path.join(latest_06, pattern), recursive=True):
                if os.path.isfile(file_path):
                    shutil.copy(file_path, APP_DATA_DIR)

    # 🌟 新增：同步 07 (NLI立场推断图表)
    latest_07 = get_latest_dir("data_07*")
    if latest_07:
        for pattern in ["**/*.html", "**/*.csv"]:
            for file_path in glob.glob(os.path.join(latest_07, pattern), recursive=True):
                if os.path.isfile(file_path):
                    shutil.copy(file_path, APP_DATA_DIR)

    # 同步 08 (话题挖掘图表)
    latest_08 = get_latest_dir("data_08*")
    if latest_08:
        for pattern in ["figs/*.html", "*.csv"]:
            for file_path in glob.glob(os.path.join(latest_08, pattern), recursive=True):
                if os.path.isfile(file_path):
                    shutil.copy(file_path, APP_DATA_DIR)
                    
    return latest_06, latest_07, latest_08

latest_06_dir, latest_07_dir, latest_08_dir = sync_assets_to_app_data()
APP_DATA_DIR = "./app_data"

# --- 3. 侧边栏：全局控制与导航 ---
st.sidebar.header("🎯 Navigation")

# 🌟 重命名：更加专业、高阶的业务大屏标签名
current_view = st.sidebar.radio(
    "👁️ 选择数据视图 (Select View):",
    [
        "📊 1. Macro Sentiment & Stance (大盘情绪与公众立场)", 
        "☢️ 2. Crisis Attribution & Deep Dive (危机归因与话题挖掘)"
    ]
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 一键同步最新数据 (Refresh)"):
    sync_assets_to_app_data.clear() 
    st.rerun()                      

st.sidebar.markdown("---")
if latest_06_dir:
    st.sidebar.success(f"📂 06 情绪大盘已挂载:\n`{os.path.basename(latest_06_dir)}`")
if latest_07_dir:
    st.sidebar.success(f"📂 07 立场推断已挂载:\n`{os.path.basename(latest_07_dir)}`")
if latest_08_dir:
    st.sidebar.success(f"📂 08 话题归因已挂载:\n`{os.path.basename(latest_08_dir)}`")

# --- 4. 无缝自适应加载 HTML 函数 ---
def load_html_chart(file_name, height=750):
    path = os.path.join(APP_DATA_DIR, file_name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            html_data = f.read()
            
        responsive_css = "<style>body { margin: 0 !important; padding: 0 !important; overflow: hidden !important; }</style>"
        if "<head>" in html_data:
            html_data = html_data.replace("<head>", f"<head>{responsive_css}")
        else:
            html_data = responsive_css + html_data
            
        components.html(html_data, height=height, scrolling=False)
    else:
        st.warning(f"图表未生成或丢失: {file_name}")

def load_csv_data(file_name):
    path = os.path.join(APP_DATA_DIR, file_name)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

# --- 5. 动态渲染选中页面 ---

if current_view == "📊 1. Macro Sentiment & Stance (大盘情绪与公众立场)":
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

elif current_view == "☢️ 2. Crisis Attribution & Deep Dive (危机归因与话题挖掘)":
    st.header("Crisis Topic Modeling & Attribution")
    st.markdown("*注：基于高维语义聚类与 C-TF-IDF，精准定位高危专属软肋与毒性传播源。内部的优先级计算已自动融合 NLI 立场偏好。*")

    # 🌟 将 NLI 立场推断图无缝嵌入在这里，作为“大盘情绪表象”到“真实立场基本盘”的过渡！
    st.subheader("Audience Stance Breakdown (NLI Zero-Shot)")
    st.markdown("*注：基于大语言模型自然语言推理（NLI），透过极端情绪表象，剥离出评论区真实的攻击者、路人与品牌辩护者占比。*")
    load_html_chart("06_nli_stance_distribution_stacked.html", height=500)
    st.divider()

    st.subheader("Radar: Topic Negativity × Amplification")
    load_html_chart("01_topic_bubble_netneg_x_amp.html", height=750)
    st.divider()

    st.subheader("🎯 Exclusive Risk (品牌专属靶点)")
    st.markdown("*超标率：只有我方阵营在讨论，竞品极少提及。*")
    load_html_chart("02_topic_lift_bar_primary.html", height=800)
    st.divider()
        
    st.subheader("☢️ Priority Ranking (Stance-Aware)")
    st.markdown("*综合立场、情绪和声量的优先处理等级。*")
    load_html_chart("03_priority_ranking_stance_aware.html", height=900)
    st.divider()
    
    st.subheader("📊 Attribution Risk Matrix")
    st.markdown("*矩阵透视：精准拆解每个话题在不同评价维度的攻击强度。*")
    load_html_chart("04_attribution_risk_matrix.html", height=750)
    st.divider()
