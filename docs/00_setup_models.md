# 🛠️ Module 00 — Model Registry & Offline Inference Foundation (v2: Sentiment-5 Intensity)

> **不考虑旧管线兼容**：本项目情感分析从此以 **5 档情绪烈度（Sentiment-5）** 作为全链路唯一标准输出；后续 04/05/06/07 将围绕该标准重新设计数据契约与指标体系。

---

## 0. 模块定位与目标

### 0.1 模块定位
Module 00 是全项目的 **模型供应链 / 推断基础设施层（Inference Layer）**，负责：
- 统一下载并固化所有模型权重到本地
- 锁定模型版本（revision/commit），保证跨时间复跑一致
- 输出可审计的 manifest 与离线 smoke test 报告
- 明确“模型输出契约”，从源头杜绝将 softmax `max_prob` 误当“强度/共识”的问题

### 0.2 核心目标（必须满足）
1. **可复现（Reproducible）**：模型版本 pin 到 revision，并记录依赖版本（torch/transformers/python）
2. **可离线（Offline-ready）**：断网 + `local_files_only=True` 下能加载并完成推断
3. **可审计（Auditable）**：输出模型来源、license、revision、文件清单/校验信息、smoke test 结果
4. **契约优先（Contract-first）**：强制规范 Sentiment-5 的输出字段，确保后续统计/机制研究口径一致

---

## 1. 输入（Inputs）

### 1.1 配置文件（建议新增：单一真相源）
`configs/model_registry.yaml`

建议字段（示意）：
- `hf_endpoint`: 可选（镜像/代理）
- `runtime_profile`: `cpu_int8 | xpu | openvino`
- `models`:
  - `model_key`
  - `repo_id`
  - `revision`  # 必须 pin（commit hash 或 tag）
  - `local_dir`
  - `task`: `sentiment5 | embedding | summarization | vad(optional)`
  - `expected_files`（可选）

### 1.2 环境变量（可选覆盖）
- `HF_ENDPOINT`（镜像/代理）
- `HF_HOME` / `TRANSFORMERS_CACHE`（缓存目录）
- `HF_HUB_DISABLE_TELEMETRY=1`（建议默认关闭）
- `TRANSFORMERS_OFFLINE=1` / `HF_HUB_OFFLINE=1`（离线验证阶段启用）

---

## 2. 输出（Outputs / Artifacts）

> 00 不仅“下载模型”，还必须输出“证据”，证明模型在本机可离线推理。

### 2.1 模型本地资产
- `models/<model_key>/...`（权重、tokenizer、config 等）

### 2.2 模型审计清单（必备）
- `models/manifest.json`  
  至少包含：
  - `model_key`
  - `repo_id`
  - `revision`
  - `downloaded_at`
  - `license`（可从 HF metadata 解析写入）
  - `python_version / torch_version / transformers_version`
  - `local_path`
  - `files`（可选：关键文件列表、hash）

### 2.3 离线连通性报告（必备）
- `reports/00_smoke_test.json`
  - `load_ok` / `inference_ok`
  - `device`（cpu/xpu/openvino）
  - `latency_ms`
  - `notes`（异常原因、fallback 行为）

### 2.4 可选：性能基准报告（建议）
- `reports/00_benchmark.csv`
  - `profile, model_key, texts_per_sec, p50_ms, p95_ms`

---

## 3. 模型套件（Model Suite）

### 3.1 Sentiment-5（主力：5 档情绪烈度/极性）

#### 3.1.1 默认模型（推荐）
- `cardiffnlp/twitter-roberta-base-topic-sentiment-latest`

> 注意：这是 **target-based sentiment**，输入需要拼接 `target`。  
> `target` 的策略（固定 target / 多 target / AB 对照）属于 **Module 04/Config 层**；Module 00 只负责固化模型与规定输入模板。

#### 3.1.2 输入契约（必须写死）
- `text_input = "<comment_text> </s> <target>"`

#### 3.1.3 输出契约（必须写死，后续模块统一遵守）
对每条 comment 的一次推断，必须落盘以下字段：

- `sent5_label`：5 档标签（字符串）
- `sent5_probs`：长度=5 的概率向量（必须保存全量）
- `sent5_valence_expected`：连续极性（建议用期望值）
  - 设定权重向量 `w = [-2, -1, 0, +1, +2]`
  - `sent5_valence_expected = Σ(sent5_probs[i] * w[i])`
- `sent5_extremity`：情绪烈度（强度）
  - `sent5_extremity = abs(sent5_valence_expected)`
- `sent5_uncertainty`：不确定性（建议 entropy）
  - `H(p) = -Σ p_i log(p_i)`
- `sent5_target`：本次推断使用的 target（用于审计与解释）

> **硬规则**：禁止将 `max(sent5_probs)` 直接解释为“情绪强度/共识度”。  
> - 强度：用 `sent5_extremity`  
> - 不确定性：用 `sent5_uncertainty`

---

### 3.2 Embedding（用于 Topic Clustering 的语义向量）

#### 3.2.1 默认模型
- `sentence-transformers/all-MiniLM-L6-v2`

#### 3.2.2 输出契约
- `embedding_dim == 384`
- 向量无 `NaN/Inf`
- 支持 CPU-only 推断（默认）

---

### 3.3 Summarization（用于 Topic Label / Executive Phrasing）

#### 3.3.1 默认模型
- `sshleifer/distilbart-cnn-12-6`

#### 3.3.2 使用定位（必须写进文档）
- 仅用于“话题标签/短句洞察”（label / phrasing）
- **不得作为事实结论引用**（避免生成式幻觉造成研究越界）

#### 3.3.3 输出契约（建议）
- `topic_label_text`：生成的标签/摘要
- `source_comment_ids`：用于生成的代表评论 ID 列表（可追溯）

---

### 3.4 Optional Enhancement Pack（可选增强，不强制）

#### VAD 回归（连续情绪维度）
- `RobroKools/vad-bert`
- 输出：`valence / arousal / dominance`（连续值）

> 用途：作为更学术的连续强度/唤醒度特征，与 Sentiment-5 的离散烈度互补。

---

## 4. 模型下载与版本锁定策略（必须项）

### 4.1 统一下载器（强制统一）
所有模型统一使用：
- `huggingface_hub.snapshot_download()`

统一参数建议：
- `revision=<pinned_commit_hash_or_tag>`（必须 pin）
- `resume_download=True`（断点续传）
- `local_dir_use_symlinks=False`（Windows 兼容）

### 4.2 版本锁定（必须）
- 禁止仅依赖 `latest` 而不记录 revision
- 每次升级模型版本必须：
  1) 修改 `model_registry.yaml` 的 revision
  2) 重生成 `models/manifest.json`
  3) （建议）追加 `CHANGELOG.md`

---

## 5. Runtime Profiles（设备与性能策略）

> 00 负责定义 profile 与验证 profile 是否可用；大规模推断优化（batch/量化）可在 04 深化实现。

### Profile A：`cpu_int8`（默认主线）
- CPU 推断（后续可在 04 做动态量化 + micro-batching）
- 优点：依赖最少、最适合 GitHub 复现

### Profile B：`xpu`（可选）
- Intel 核显/XPU 推断（作为 optional acceleration）
- 建议在 README 里写成可选路径，不作为默认依赖

### Profile C：`openvino`（可选）
- 作为部署向展示：统一 CPU/GPU/NPU 推断入口

---

## 6. 质量门禁（Smoke Tests / Quality Gates）

00 模块下载完成后必须自动执行并落盘 `reports/00_smoke_test.json`：

1) **Offline Load Test**
- 设置 `TRANSFORMERS_OFFLINE=1`
- 使用 `local_files_only=True` 从本地路径加载全部模型

2) **Minimal Inference Test**
- Sentiment-5：
  - 输出 `sent5_probs` 且 `sum≈1`
  - 输出 `sent5_valence_expected / extremity / uncertainty`
- Embedding：
  - 输出向量维度=384
- Summarization：
  - 输出非空文本（限制 `max_new_tokens` 防 OOM）

3) **File Integrity Test**
- 检查关键文件存在（config/tokenizer/weights）
- 失败则 **PIPELINE BLOCKED**（阻断下游）

---

## 7. 下游接口契约（对 04/05/06/07 的硬约束）

### 7.1 Module 04（情感推断）必须输出
- `sent5_label`
- `sent5_probs`
- `sent5_valence_expected`
- `sent5_extremity`
- `sent5_uncertainty`
- `sent5_target`

### 7.2 Module 05（统计与机制研究）禁止事项
- 不允许把 `max_prob` 当作“强度/共识”
- 若需要“共识/一致性”，应在 **群体层** 定义（例如：video/topic 层分布熵、极化指标等）

### 7.3 Module 07（主题/摘要）规范
- summarizer 输出仅用于“标签/洞察短句”
- 报告引用必须可追溯到原评论（representative docs / golden quotes）

---

## 8. 工程化落地（Notebook → Script）

建议将 00 收敛为脚本（notebook 仅保留展示）：
- `src/setup_models.py`

CLI 示例：
- `python -m src.setup_models --config configs/model_registry.yaml --profile cpu_int8`
- `python -m src.setup_models --smoke-test --offline`

GitHub 建议：
- `models/` 默认 `.gitignore`
- 提交 `configs/model_registry.yaml`、`models/manifest.json`、`reports/00_smoke_test.json` 作为“可复现证据资产”
