# 🎯 Module 01 (v2) — YouTube Video Candidate Sourcing & Metadata (2×2 对照版｜无 run_id)

---

## 0. 模块目标

### 工业目标（展示导向）
在配额可控的前提下，通过 YouTube Data API v3：
- 检索与四个实验 cell 高相关的视频候选池
- 拉取视频级元数据（时长、发布时间、view/like/commentCount 等）
- 做质量门禁、去重、污染/冲突处理
- 输出“可直接用于抓评论+回复”的最终视频清单与审计报告

### 学术目标（设计导向）
把原本“三组对照”升级为 **2×2（Brand × Topic）**，减少“品牌效应”和“议题效应”混淆，并尽量控制视频层混杂因素（shorts、评论量过低、非公开、讨论不活跃等）。

## Environment Setup
本项目严格遵循环境变量隔离原则。请在项目根目录创建一个 `.env` 文件，并注入您的 YouTube Data API v3 凭证：
YOUTUBE_API_KEY="AIzaSy_YOUR_KEY_HERE"
(注：请确保 .env 文件已加入 .gitignore 以防止密钥泄露)
---

## 1. 2×2 实验设计（新的 groups schema）

### 因子定义
- Brand（品牌因子）
  - **SHEIN**
  - **NON_SHEIN**（一组快时尚品牌集合，由 config 控制，例如 Zara/H&M/Forever21/FashionNova…）
- Topic（议题因子）
  - **LABOR**（modern slavery/forced labor/sweatshop/labor exploitation…）
  - **ENV**（pollution/landfill/waste/sustainability/greenwashing…）

# 🎯 Module 01: 2×2 析因实验设计与 YouTube 核心视频资产寻址管线 (2x2 Factorial Video Sourcing & Asset Pipeline)

> **🎯 模块业务与学术目标：**
> - **学术升级 (The 2x2 Factorial Design)**：彻底摒弃存在混杂偏误的“三组对照”，将研究架构升级为严谨的 **`品牌 (SHEIN vs. Non-SHEIN)` × `议题 (Labor vs. Environment)`** 2×2 析因矩阵。从而剥离“品牌主效应”与“议题主效应”，为验证交互效应（即特定品牌在特定议题下是否被算法/情绪特殊放大）提供坚实的统计学底座。
> - **工业落地 (Data Engineering)**：在 YouTube Data API v3 每日 10,000 Quota 的严格约束下，通过批处理与指数退避，产出高质量、高互动量的靶向视频清单，作为 02 模块“Top-level 评论抓取”的绝对输入源。

---

### 📌 核心 2×2 实验矩阵定义 (The Factorial Matrix)
为确保控制变量的极致对称，我们将靶向空间划分为以下四大核心阵营（Cells）：
* 🔴 **`shein_labor` (风暴眼)**：SHEIN + 劳工指控 (e.g., *shein sweatshop, shein modern slavery*)
* 🟢 **`shein_env` (品牌护城河测试)**：SHEIN + 环保指控 (e.g., *shein pollution, shein clothing waste*)
* 🔵 **`non_shein_labor` (议题底噪)**：竞品/行业 + 劳工指控 (e.g., *fast fashion sweatshop, zara labor conditions*)
* 🟡 **`non_shein_env` (宏观基准线)**：竞品/行业 + 环保指控 (e.g., *fast fashion environmental impact*)

---

### ⚙️ 管线架构与节点职责 (Pipeline Architecture & Cell Responsibilities)

#### 🔌 Cell 1 & 2 - 引擎初始化与 API 动态调度池 (Infrastructure & Quota Management)
* **职责**：
  1. 挂载 `pyprojroot` 确立工程绝对路径，加载 `.env` 密钥池。
  2. 构建带有 **指数退避 (Exponential Backoff)** 的 API 请求包装器，有效防御 HTTP 403 (Quota Exceeded) 与 429 (Too Many Requests) 阻断。
* **📊 API 成本精算 (Quota Math)**：
  * `search.list` 每页耗费 100 Quota。设定 4 个 Cell × 每个 Cell 5 个 Query × 抓取前 2 页 = 4000 Quota。
  * `videos.list` (富化元数据) 批量请求每次仅耗费 1 Quota。
  * **工程结论**：单次完整寻址最高消耗 ~4500 Quota，远低于 10,000 的日限额，架构具备极高的横向扩展可行性。

#### 📜 Cell 3 - 战略检索配置装载 (Strategic Configuration Loading)
* **职责**：将 2×2 矩阵的搜索策略与代码解耦，读取外部 `config/youtube_search.yaml`。确保未来若需扩展至新的品牌（如 Temu），只需修改 YAML 文件而无需触碰底层逻辑。

#### 🕷️ Cell 4 & 5 - 核心寻址引擎定义 (Search Engine Definition)
* **职责**：构建 `search_videos` 原子函数。
* **过滤契约**：在请求发起侧强制附加 `type="video"` 与 `relevanceLanguage="en"` 参数，从源头确保抓取候选人（Candidates）的介质与语言纯洁性。

#### 🚀 Cell 6 - 自动化检索与血缘记录流水线 (Automated Sourcing & Data Lineage)
* **职责**：遍历 YAML 中的 4 大阵营与对应 Queries，执行分页检索。
* **数据血缘 (Data Lineage)**：在落地为 DataFrame 时，强制附加 `source_query` 与 `cell_id` 字段。确保哪怕最终数据混合在一起，也能随时追溯该视频是由哪个关键词触发的。

#### 📊 Cell 7 - 元数据富化与工业级质量门禁 (Metadata Enrichment & Quality Gates)
* **职责**：提取候选视频的 `viewCount`, `likeCount`, `commentCount`, `duration`。
* **🛡️ 质量门禁 (Quality Gates)**：执行面向下游 02 模块“Top-level 评论抓取”的硬性防线：
  1. `duration_min >= 3`：物理级剔除 YouTube Shorts（规避短视频评论区无价值的短句情绪发泄）。
  2. `commentCount >= 100`：确保该视频拥有足够深度的互动池，防止下游大模型算力浪费在“死水视频”上。
  3. `privacyStatus == public`。

#### 🚨 Cell 8 - 交叉污染阻断与人工干预机制 (Contamination & Human-in-the-loop)
* **核心难点**：深度纪录片极易同时命中多个 Cell（如既谈劳工又谈环保），摧毁 2×2 矩阵的独立性假设。
* **处理策略**：
  1. **自动化隔离 (Exclude Policy)**：通过全局 `video_id` 聚合统计，将跨 Cell 命中的视频剥离并导出至 `video_conflicts.csv`。
  2. **HITL (Human-in-the-loop)**：支持研究员离线审查冲突资产，通过配置白名单将其强制回调至“主导阵营 (Dominant Cell)”，确保高价值纪录片不被误杀。

#### ⚖️ Cell 9 - 基线截断与样本对齐 (Baseline Thresholding)
* **职责**：由于 YouTube 流量呈极端长尾偏态，传统的 PSM（倾向性评分匹配）或分层抽样极易导致“无共同支撑域 (No Common Support)”从而使样本枯竭。
* **降噪工程**：采用 IQR 离群值截断法（或百分位截断），剔除播放量极低（无人问津）或极高（全局顶流，往往伴随大量粉丝刷榜干扰）的异常视频，确保四大阵营在曝光基数（Exposure Baseline）上处于合理的同一量级。

#### 💾 Cell 10 - 资产持久化与契约移交 (Asset Persistence & Handoff)
* **职责**：
  1. 动态生成时间戳输出目录（`data_01_video_candidates_YYYYMMDD_HHMMSS`）。
  2. 输出 02 模块的唯一合法输入源 `01_video_candidates_final.csv`。
  3. 打印 2×2 矩阵最终入库视频分布的总结报表，完成管线交接。

