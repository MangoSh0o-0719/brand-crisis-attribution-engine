# Brand Crisis Attribution Engine：品牌危机归因分析引擎

一个面向社交媒体品牌危机诊断的端到端 **NLP 分析项目**。本项目以 **Shein 劳工争议** 为案例，基于 **2×2 对照研究设计**（目标品牌 vs. 对照品牌；危机话题 vs. 中性话题），从 YouTube 评论原始文本出发，逐步完成情绪识别、立场推断、议题聚类、风险归因和优先级排序，并最终输出可用于业务判断的可视化结果与交互式仪表盘。

---

## 在线Dashboard

[点击查看 Streamlit Dashboard](https://brand-crisis-attribution-engine-lc8po9zmaamwmkulfse5cc.streamlit.app/)

---

## 项目交付物

- **项目报告（PDF）**：`reports/Changyu_BrandCrisis_Analytics_Portfolio.pdf`
- **交互式仪表盘**：上方 Streamlit 应用
- **代码与分析 Notebook**：当前仓库

---

## Dashboard 预览

<img width="2696" height="1356" alt="image" src="https://github.com/user-attachments/assets/8b25cd39-ce7a-4d8f-914b-baa1a76857eb" />
<img width="2787" height="1170" alt="dashboard_2" src="https://github.com/user-attachments/assets/42f568fb-b1da-4c08-a26e-d94381081f9f" />
<img width="2850" height="1328" alt="dashboard_3" src="https://github.com/user-attachments/assets/d71bb2f3-3990-48ad-b221-3a8221e418e6" />

---

## 项目概述

本项目是一个面向品牌危机诊断的端到端文本分析流程。不同于只停留在“负面情绪多不多”的描述层面，本项目更关注一个更具业务决策价值的问题：

> **哪些风险只是噪音，哪些风险既容易被放大，又容易被稳定归因到品牌本身？**

围绕这个问题，项目从 YouTube 评论抓取与清洗开始，逐步完成：

- **宏观风险验证**
- **高风险议题识别**
- **品牌专属性归因分析**
- **讨论升级机制诊断**
- **响应优先级排序**

项目完整的业务分析写作见报告：  
`reports/Changyu_BrandCrisis_Analytics_Portfolio.pdf`

---

## 关键发现 Key Findings

- **Shein 在劳工争议语境下呈现出显著更高的综合风险水平**，相较于对照组并非单纯的负面噪音堆积，而是存在真实的危机增量。
- **议题层面的高风险主题**主要集中在劳工剥削、拒购/消费阻断、网红洗白反噬，以及围绕快时尚价值观的冲突讨论。
- **高风险议题往往伴随支持声稀缺、对立结构更强的讨论特征**，这意味着与其直接对线，更适合通过证据材料、第三方背书和 FAQ 型内容来进行回应。

---

## 分析框架 Analytical Framework

本项目并不把品牌危机简单理解为“负面情绪上升”，而是进一步拆成四个更贴近业务判断的问题层：

### 1. Impact（影响强度）
哪些议题既负面，又具有较强的放大潜力？

### 2. Attribution（品牌归因）
哪些风险更容易被认为是“品牌自身问题”，而不是行业共性问题？

### 3. Dynamics（讨论机制）
讨论是通过共鸣扩散，还是通过对立和极化不断升级？

### 4. Priority（响应优先级）
综合负面程度、放大潜力、品牌归因性和争议结构后，哪些议题应该优先处理？

这一框架对应了最终报告的分析路径：  
从**宏观验证**，到**议题层风险地图**，再到**升级机制诊断**，最后形成**行动优先级判断**。

---

## 项目输出内容 What the Pipeline Produces

项目最终输出了多类可视化结果和交互式图表，包括：

- **Topic Bubble Landscape**  
  议题净负面程度 × 议题放大潜力

- **Lift Ranking Bar Chart**  
  最容易被归因到品牌本身的议题排序

- **Priority Ranking**  
  基于负面程度、放大性、立场结构、争议度和议题热度的综合优先级排序

- **Attribution Risk Matrix**  
  品牌归因性 × 处理优先级的风险矩阵，并叠加争议度与议题热度信息

- **NLI Stance Distribution**  
  Support / Oppose / Neutral 立场分布，用于观察讨论中的共鸣与对立结构

这些输出共同服务于几个核心问题：

1. 危机是否在结构上显著高于基线？
2. 哪些议题最容易扩散？
3. 哪些议题最容易被记成“品牌专属风险”？
4. 为什么有些讨论更容易升级？
5. 品牌应该优先回应什么？

---

## 端到端分析流程 End-to-End Pipeline

<img width="1748" height="1956" alt="研究框架" src="https://github.com/user-attachments/assets/7c0dd1a9-eee3-400c-8e99-d74042af1e2d" />
---

## 仓库结构 Repository Structure

- `Notebooks/` —— 按推荐顺序排列的分析 Notebook（`00–08`）
- `configs/` —— YouTube 搜索配置、清洗词典、模型注册表等配置文件
- `Data/` —— 从原始抓取到分析输出的分阶段时间戳文件夹
- `app_data/` —— Dashboard 使用的 HTML 图表和 CSV 结果表
- `reports/` —— 项目报告与展示材料
- `models/` —— 本地模型快照，用于离线复现（不建议直接上传到 GitHub）

---

## Notebook 流程说明

### `00_setup_models.ipynb`
下载并锁定本地模型快照，支持后续离线运行。

### `01_youtube_video_candidate.ipynb`
构建 2×2 对照矩阵，并导出候选视频列表。

### `02_comment_scraper.ipynb`
使用多 API key 轮换抓取评论与回复，并重建 thread 结构。

### `03_comment_cleaning.ipynb`
完成文本标准化与清洗，生成模型输入和展示用文本字段。

### `04_sentiment_analysis.ipynb`
运行 5 分类情绪预测，生成可用于后续统计分析的情绪结果。

### `05_scorecard.ipynb`
按视频聚合核心指标，并通过 weighted bootstrap 估计不确定性区间。

### `06_dashboard_html.ipynb`
生成 KPI 卡片、统计图表和 Dashboard 所需 HTML 可视化内容。

### `07_thread_stance_nli.ipynb`
运行 zero-shot NLI，对回复与父评论之间的立场关系进行推断，并计算共鸣度与争议度。

### `08_topic_modeling.ipynb`
完成议题聚类、Lift 品牌归因分析和考虑立场结构的优先级排序。

---

## 如何运行 How to Run

### 1. 创建环境并安装依赖
```bash
python -m venv .venv
# activate your virtual environment
pip install -r requirements.txt
```

### 2. 配置文件
- 编辑 `configs/youtube_search.yaml`
- 可选编辑 `configs/cleaning_lexicon.yaml`
- 可选编辑 `configs/model_registry.yaml`

### 3. 下载模型
先运行：

- `Notebooks/00_setup_models.ipynb`

### 4. 按顺序执行 Notebook
依次运行 `01` 到 `08`。  
每个阶段都会在 `Data/` 目录下生成带时间戳的输出文件夹。

---

## 项目报告 Report

本项目的业务分析报告位于：

- `reports/Changyu_BrandCrisis_Analytics_Portfolio.pdf`

报告内容包括：

- 项目背景与研究问题
- 2×2 研究设计
- 宏观风险验证
- 议题层风险识别
- 品牌专属性归因分析
- 讨论升级机制诊断
- 响应优先级与策略建议
- 指标说明、清洗规则与模型工具补充说明

---

## 可复现性说明 Reproducibility Notes

- 每次运行都会写入带时间戳的 `Data/data_XX_*` 文件夹
- 模型版本可以通过配置文件与 lockfile 固定
- 仓库结构支持从原始评论到最终图表的完整追踪

---

## 隐私与合规 Privacy & Compliance

- 如果涉及平台政策或仓库体积限制，不建议直接提交原始抓取评论
- API key 请务必保存在本地，并通过 `.gitignore` 排除
- 建议使用 `.env` 管理本地密钥和敏感配置

---
