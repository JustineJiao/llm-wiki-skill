---
name: llm-wiki
version: 1.2.0
author: JYS (adapted for WorkBuddy)
license: MIT
description: 知识库构建（wiki/消化/查询/健康检查/图谱/结晶化）| 多源素材消化与分析。其他 skill（如 clippings-digest）通过此 skill 的 ingest 工作流完成消化。
---

# llm-wiki — 个人知识库构建系统

## 核心理念

知识库的价值：知识编译一次，持续维护，而不是每次重新推导。

## 模板文件

位于 `templates/` 目录，生成 wiki 页面时读取对应模板后填充：
`source-template.md` · `entity-template.md` · `topic-template.md` · `query-template.md` · `synthesis-template.md` · `review-template.md`

---

## 可选依赖 skill

| 依赖 | 用途 | 回退方案 |
|------|------|---------|
| `baoyu-url-to-markdown` | 网页/X/YouTube 提取 | WebFetch |
| `wechat-article-search` | 公众号检索 | 用户手动粘贴 |
| `markdown-converter` | PDF/DOCX 转 Markdown | Read 直接读取 |

缺失不阻塞核心流程，自动降级为原生工具。

---



## 工作流总览

**不触发**：仅要求"总结这篇文章"时。

| 用户意图关键词 | 工作流 |
|---|---|
| "初始化知识库"、"新建 wiki" | **init** |
| URL / 文件路径 / "消化"、"整理" | **ingest** |
| "批量消化" / 给了文件夹路径 | **batch-ingest** |
| "关于 XX"、"查询" | **query** |
| "给我讲讲 XX"、"深度分析"、"综述" | **digest** |
| "对比一下 X 和 Y" / "整理时间线" | **digest**（特殊格式） |
| "检查知识库"、"健康检查"、"lint" | **lint** |
| "知识库状态"、"有多少素材" | **status** |
| "知识图谱"、"知识库地图" | **graph** |
| "删除素材"、"移除" | **delete** |
| "待审"、"review items" | **reviews** |
| "结晶化"、"把对话记进知识库" | **crystallize** |

**重要**：如果用户直接给了一个 URL 或文件，但没有明确说要做什么，默认走 **ingest** 工作流。如果知识库还不存在，先自动走 **init** 再走 **ingest**。

---

## 通用前置检查

除 `init` 外，其他工作流默认先执行这段检查：

1. 先检查**当前工作目录**（`d:\Program Files\WorkBuddyDir`）是否包含 `.wiki-schema.md`
   - 如果包含 → 用当前目录作为知识库根路径
   - 如果不包含 → 回退到读取 `~/.llm-wiki-path`（`C:\Users\13986\.llm-wiki-path`）
2. 如果两者都没有：
   - `ingest` / `batch-ingest` → 先运行 `init`
   - `query` / `lint` / `status` / `digest` / `graph` / `delete` → 提示用户先初始化知识库
3. 读取知识库根目录下的 `.wiki-schema.md`
4. 从 `.wiki-schema.md` 的"语言"字段判断 `WIKI_LANG`
   - `语言：中文` → `WIKI_LANG=zh`
   - `语言：English` → `WIKI_LANG=en`
   - 字段缺失 → 默认 `WIKI_LANG=zh`

## 输出语言规则

所有面向用户的输出和新写入的 wiki 内容，都按 `WIKI_LANG` 生成：

- `WIKI_LANG=zh` → 使用中文
- `WIKI_LANG=en` → 使用英文
- 文件路径、wiki 链接、目录名保持现有约定

**术语对照**：
| 中文 | English |
|------|---------|
| 素材 | Source |
| 实体 | Entity |
| 主题 | Topic |
| 摘要 | Summary |
| 综合 | Synthesis |
| 消化 | Ingest |
| 对比 | Comparison |
| 深度报告 | Deep Dive Report |
| 知识图谱 | Knowledge Graph |

---

## Token 优化策略

Ingest 和 batch-ingest 工作流遵循 Two-Step CoT 模式：Step 1 完整阅读原素材得到分析 JSON，Step 2 只基于分析 JSON 生成页面（不重复读原素材）。预算分配、部分读取规则、SHA256 缓存详见 `references/token-optimization.md`。

---

批量消化时，所有文件完成后执行一次交叉综合。完整步骤见 `references/batch-cross-synthesis.md`。

---

## 工作流 1：init（初始化知识库）

### 前置检查

1. 执行**通用前置检查**
2. 如果通用前置检查找到了知识库 → 提示用户已存在并询问是否重新初始化
3. 如果 `~/.llm-wiki-path` 存在但当前目录不是知识库 → 提示用户已有知识库，询问新建还是切换
4. 两个都没有 → 进入初始化流程

### 步骤

1. **询问知识库主题**：
   - "你的知识库要围绕什么主题？比如'AI 学习笔记'、'产品竞品分析'、'读书笔记'"
   - 如果用户没想法，默认用"我的知识库"

2. **询问知识库语言**：
   - "知识库内容用什么语言？中文 / English（默认中文）"
   - 选项：`zh`（中文）或 `en`（English）
   - 如果用户没有明确说，默认 `zh`

3. **询问保存位置**：
   - 默认：`~/Documents/我的知识库/`（zh）或 `~/Documents/my-wiki/`（en）
   - 用户可以自定义路径，如 `D:\知识库\玉米知识库`

4. **创建目录结构**（用 Write 工具创建每个文件）：
   ```
   知识库路径/
   ├── raw/
   │   ├── articles/       # 网页文章
   │   ├── tweets/         # X/Twitter
   │   ├── wechat/         # 微信公众号
   │   ├── xiaohongshu/    # 小红书
   │   ├── zhihu/          # 知乎
   │   ├── pdfs/           # PDF
   │   ├── local/          # 本地文件
   │   └── assets/         # 图片等附件
   ├── wiki/
   │   ├── entities/       # 实体页
   │   ├── topics/         # 主题页
   │   ├── sources/        # 素材摘要
   │   ├── synthesis/      # 综合分析
   │   ├── comparisons/    # 对比分析
   │   ├── queries/        # 查询记录
   │   └── reviews/        # 待审项（人机协作）
   ├── purpose.md          # 研究方向与目标
   ├── index.md            # 索引
   ├── log.md              # 操作日志
   ├── overview.md         # 执行摘要
   └── .wiki-schema.md     # 配置文件
   ```

5. **创建 `.wiki-schema.md`**（知识库配置文件）：
   ```yaml
   ---
   主题: <用户指定的主题>
   语言: 中文 | English
   创建日期: YYYY-MM-DD
   别名词表:  # query/digest 时用于别名展开
     LLM:
       - 大语言模型
       - 大模型
     GS:
       - 基因组选择
       - genomic selection
   ---
   ```

6. **将路径写入 `~/.llm-wiki-path`**（用 Write 工具）

7. **创建 `purpose.md`**：请用户填写研究目标、关键问题和研究范围

8. **输出引导说明**（按 `WIKI_LANG` 切换）：

**zh**：
```
知识库已创建！路径：<路径>

接下来你可以：
- 给我一个链接，我会自动提取并整理（网页、X/Twitter、公众号等）
- 给我一个本地文件路径（PDF、Markdown 等）
- 直接粘贴文本内容
- 批量消化：给我一个文件夹路径

推荐：用 Obsidian 打开这个文件夹，可以实时看到知识库的构建效果。
```

---

## 工作流 2：ingest（消化素材）

Token 优化详细策略见 `references/token-optimization.md`。

### 前置检查

执行**通用前置检查**。

### 素材提取路由

根据素材类型选择 WorkBuddy 原生工具：

**URL 类素材**：
- 通用网页 → 用 `WebFetch`（内容转为 Markdown）
- X/Twitter → 优先用 `baoyu-url-to-markdown` skill（已安装），回退 `WebSearch`
- 微信公众号 → 优先用 `wechat-article-search` skill，回退 `WebSearch`
- YouTube → 优先用 `baoyu-url-to-markdown` skill 的 youtube adapter，回退手动提示
- 知乎/小红书 → `WebFetch` 尝试，失败则提示用户手动粘贴

**本地文件**：
- `.md` / `.txt` / `.html` → `Read` 直接读取
- `.pdf` → 用 `markdown-converter` skill（markitdown）或 `Read` 直接读取
- `.docx` / `.pptx` → 用 `markdown-converter` skill

**纯文本粘贴** → 直接使用

### 内容分级处理

- 素材内容 > 1000 字 → **完整处理**
- 素材内容 ≤ 1000 字 → **简化处理**

### 完整处理流程（长素材 > 1000 字）

1. **提取素材内容**：按上面的路由获取素材文本。

2. **保存原始素材**到 `raw/` 对应目录（用 `Write` 工具）：
   - 文件名格式：`{日期}-{短标题}.md`
   - URL 素材在文件头部记录原始 URL
   - **图片检测**：扫描内容中是否包含图片引用（`![` 或 `<img` 或图片 URL）。如果检测到图片：
     - 告诉用户："素材包含 {N} 张图片引用。图片链接可能失效，建议手动下载到 `raw/assets/`"
     - 在后续 source 页面的 frontmatter 中记录 `images: {N}` 和 `image_paths: []`
     - 不阻塞 ingest 流程

3. **读取上下文**：
   - 优先顺序：`purpose.md` > `.wiki-schema.md` > `index.md`
   - 如果 `purpose.md` 存在，先读取核心目标和关键问题

4. **缓存检查（AI 级）**：
   - 计算原始素材文件的 SHA256 哈希值
   - 检查知识库根目录的 `.wiki-cache.json` 中是否有相同哈希值
   - 如果命中 → 跳过 LLM 处理，直接复用已有结果
   - 如果未命中 → 继续流程
   - 缓存文件格式：`{"<raw_file_path>": "<sha256_hash>", ...}`

5. **Step 1 — 结构化分析**（输出 JSON）：
   - **输入**：原始内容 + `purpose.md` + 现有 wiki 结构（至少读取 `index.md` 概要和 `new_vs_existing.updates` 列出的已有页面）
   - **上下文预算**：源素材 40% + 现有 wiki 30% + 分析生成 20% + 系统 10%
   - **输出**：JSON 格式的分析结果，**不持久化**，只在当前 ingest 流程传递到 Step 2
   - **注意**：此步是唯一需要完整阅读原素材的环节

   ```json
   {
     "source_summary": "一句话概括",
     "entities": [
       {"name": "xxx", "type": "concept", "relevance": "high",
        "confidence": "EXTRACTED", "evidence": "原文摘录（≤50字）"}
     ],
     "topics": [{"name": "xxx", "importance": "high"}],
     "connections": [
       {"from": "A", "to": "B", "type": "因果",
        "confidence": "INFERRED", "evidence": "推理依据"}
     ],
     "contradictions": [
       {"claim_a": "...", "claim_b": "...", "context": "..."}
     ],
     "new_vs_existing": {"new_entities": [], "updates": []},
     "review_items": [
       {"type": "create_page | deep_research | skip", "description": "...",
        "reason": "为什么会触发待审", "suggested_queries": ["搜索词1", "搜索词2"]}
     ]
   }
   ```

   **置信度赋值规则**：
   | 标注 | 含义 | evidence 要求 |
   |------|------|--------------|
   | `EXTRACTED` | 原文直接陈述 | 必须，≤50字原文摘录 |
   | `INFERRED` | 从多处原文推断 | 必须，说明推理依据 |
   | `AMBIGUOUS` | 原文表述不清 | 可选 |
   | `UNVERIFIED` | 来自AI背景知识 | 可选 |

   **JSON 验证**：输出后自我检查——确保 `entities`、`topics`、`confidence` 字段都存在。如果字段缺失，回退到单步流程（不进行 Step 2，新内容统一标注 `confidence: UNVERIFIED`）。

6. **Step 2 — 页面生成**（Token 优化版）：
   - **输入**：Step 1 分析结果 JSON（**不是原素材全文**） + `purpose.md` + 需要更新的已有页面（部分读取）
   - **上下文预算**：Step 1 分析 40% + 相关已有页面 40%（部分读取） + 生成 20%
   - **关键 Token 节省**：此步不再读取原素材全文，只依赖 Step 1 的结构化分析
   - **页面部分读取**：对 `new_vs_existing.updates` 列出的已有页面，只读前 500 字 + YAML frontmatter；超 2000 字的页面用 grep 定位相关段落
   - **输出**：所有需要创建或更新的 wiki 页面内容，均包含完整的 YAML frontmatter

   **Review Items 生成规则**（当 Step 1 分析中存在以下情况时生成）：
   - 实体置信度为 `AMBIGUOUS` 且对知识库核心主题重要 → 生成 review 建议用户确认
   - 实体间关系为 `INFERRED` 且无直接原文支撑 → 生成 review 并预生成搜索词
   - 发现明显的知识空白（`purpose.md` 中标记的关键问题但无相关素材） → 生成 deep_research review
   - 每个 review item 按 `templates/review-template.md` 格式写入 `wiki/reviews/`

7. **生成素材摘要页**（`wiki/sources/{日期}-{短标题}.md`）：
   - 参考 `{SKILL_DIR}/templates/source-template.md` 格式
   - 包含：基本信息、核心观点、关键概念、来源引用、与其他素材的关联
   - 对 `INFERRED` / `AMBIGUOUS` 的条目，用 HTML 注释保留置信度：
     ```markdown
     <!-- confidence: INFERRED -->
     ```
   - 更新 `.wiki-cache.json`

8. **更新或创建实体页**（`wiki/entities/`）：
   - 对每个关键概念，检查是否已有对应页面
   - 已有 → 追加新信息，更新"不同素材中的观点"部分
   - 没有 → 创建新实体页，参考 `templates/entity-template.md`
   - 使用 `[[实体名]]` 语法做双向链接

9. **更新或创建主题页**（`wiki/topics/`）：
   - 如果已有对应主题页 → 更新素材汇总表
   - 没有 → 创建新主题页，参考 `templates/topic-template.md`

10. **更新 index.md**：在对应分类下添加新条目，更新概览统计数字

11. **更新 log.md**：追加 `## {日期} ingest | {素材标题}` 记录

12. **向用户展示结果**（按 `WIKI_LANG`）：
```
已消化：{素材标题}

新增页面：
- {素材摘要页}
- {新实体页1}

更新页面：
- {已有实体页2}

发现关联：
- 这篇素材和 [[已有素材]] 在 {某概念} 上有联系
```

### 简化处理流程（短素材 ≤ 1000 字）

1. **保存原始素材**到对应 `raw/` 目录（同样检测图片）
2. **读取上下文并检查缓存**
3. **生成简化摘要页**：只包含基本信息和核心观点，不写"原文精彩摘录"
4. **提取 1-3 个关键概念**：已有实体页追加一句话；没有则在摘要页用 `[待创建: [[概念名]]]` 标记
5. **更新 index.md 和 log.md**
6. 跳过主题页创建、overview 更新

---

## 工作流 3：batch-ingest（批量消化）

### 步骤

1. **确认知识库路径**：执行通用前置检查
2. **列出所有可处理文件**（`.md`, `.txt`, `.pdf`, `.html`），忽略隐藏文件和系统目录
3. **展示文件列表**，要求用户确认处理范围
4. **逐个处理**：按 `references/token-optimization.md` 的 Two-Step CoT 流程，先做缓存检查，命中则跳过
5. ** 5 个文件后暂停**，展示进度并询问是否继续，如果用户要求全部消化，则**逐个处理全部文件**
6. **全部完成后 → Batch 交叉综合**：按 `references/batch-cross-synthesis.md` 执行一次交叉综合

---

## 工作流 4：query（查询知识库）

使用 **4 阶段混合查询管线**：关键词搜索 → 图谱扩展 → 预算控制 → 上下文组装。

### Phase 1：关键词搜索（Tokenized Search）

1. **确认知识库路径**：执行通用前置检查
2. **读取 index.md** 了解全貌
3. **别名展开**：先读取 `.wiki-schema.md` 中的"别名词表"，如果用户的查询关键词命中某一组别名，将该组所有同义词纳入搜索（只在命中的组内展开，不跨组传递，自动去重）
4. **执行搜索**：
   - 在 `wiki/` 下用 `Grep/Select-String` 搜索所有关键词
   - **标题匹配加分**：文件名或页面标题含有关键词的 +10 分
   - **正文命中**：每命中一次 +1 分
   - 按总分排序，取前 10 个候选页面

### Phase 2：图谱扩展（Graph Expansion）

使用 4-Signal Relevance 模型，将 Phase 1 的前 5 个结果作为**种子节点**：

1. 读取 `wiki/` 下所有页面的 YAML frontmatter（包含 `type`, `sources[]`, 和 `[[链接]]`）
2. 对每个种子节点，找出与其相关性 ≥ 2.0 的其他页面（2-hop 遍历）
3. 距离衰减：跳数每增加 1，权重 ×0.5
4. 合并扩展结果，按综合分数排序，取前 8 个

### Phase 3：预算控制（Budget Control）

1. 按可用上下文预算分配：
   - 查询回答：40%
   - 相关页面内容：40%（按分数从高到低分配）
   - 系统指令 + 格式：20%
2. 如果总 Token 超预算，从最低分开始裁剪页面

### Phase 4：上下文组装（Context Assembly）

1. **读取最终选定的页面**：
   - 高分页面 → 读取完整内容
   - 中分页面 → 只读前 500 字 + YAML frontmatter + 命中段落
   - 低分页面 → 只读 YAML frontmatter + 命中段落
2. **组装回答**：
   - 标注信息来源（`[[页面名]]`）
   - 多观点分别列出
   - 展示搜索路径："关键词搜索 → 图谱扩展 → 检索 {N} 个相关页面"

3. **判断是否持久化**：引用 3 个及以上来源时，询问用户是否保存
4. **保存 query 页面**（如用户同意）：
   - 用 `templates/query-template.md` 生成页面
   - 保存到 `wiki/queries/{date}-{short-hash}.md`
   - 更新 index.md 和 log.md
   - 自引用防护：query 页面不纳入后续 ingest 的主来源扫描

---

## 工作流 5：lint（健康检查）

### 触发时机

- 用户主动说"检查知识库"
- 每次 ingest 后，如果素材总数是 10 的倍数，主动建议运行 lint

### 步骤

1. **确定检查范围**：
   - 最近更新的 10 个页面
   - 随机抽查的 10 个页面
   - 如果页面总数 ≤ 20，检查全部

2. **机械检查**（AI 逐项执行）：
   - **孤立页面**：`wiki/entities/` 下没有被其他页面 `[[链接]]` 引用的实体
   - **断链**：`[[X]]` 链接指向的 `X.md` 不存在
   - **index 一致性**：index.md 有记录但文件缺失 / 文件存在但 index 未记录

3. **AI 判断检查**：
   - **矛盾信息**：同一实体在不同页面描述冲突
   - **交叉引用缺失**：相关实体应互相链接但没链
   - **置信度报告**：统计 `EXTRACTED / INFERRED / AMBIGUOUS / UNVERIFIED`，高亮 `AMBIGUOUS`

4. **输出修复建议**：按 `WIKI_LANG` 输出格式化的健康检查报告

5. **询问用户**：要自动修复哪些问题？

---

## 工作流 6：status（查看状态）

### 步骤

1. **执行通用前置检查**
2. **统计**：
   - 按 `raw/` 子目录统计各来源文件数
   - `wiki/entities/`、`wiki/topics/`、`wiki/sources/`、`wiki/synthesis/`、`wiki/comparisons/` 各目录页面数
   - `purpose.md` 是否存在
3. **读取 log.md 最后 5 条记录**
4. **读取 index.md 获取主题概览**
5. **输出报告**（按 `WIKI_LANG`）：
   - 素材分布
   - Wiki 页面统计
   - 研究方向
   - 最近活动
   - 外挂状态（已安装的可选依赖 skill）
   - 优化建议（哪些主题值得深入、哪些实体值得整理）

---

## 工作流 7：digest（深度综合报告）

**区别于 query**：query 是快速问答（不生成新页面）；digest 是跨素材深度综合（生成持久化报告）。

### 步骤

1. **执行通用前置检查**
2. **执行混合搜索**（同 query 的 Phase 1-3：关键词搜索 → 图谱扩展 → 预算控制），取前 10 个相关页面
3. **根据触发关键词选择输出格式**：
   - "对比/比较" → **对比表格式**
   - "时间线/按时间" → **时间线格式**（Mermaid gantt 或纯文字）
   - 其他 → **深度报告格式**
4. **生成深度报告**，保存到 `wiki/synthesis/{主题}.md`
5. **更新 index.md 和 log.md**
6. **展示结果**

**深度报告格式**：背景 → 核心观点（附来源） → 不同视角对比 → 知识脉络 → 待解决问题 → 相关页面

**对比表格式**：维度对比表格 → 关键差异 → 相关页面

**时间线格式**：Mermaid gantt 图 + 事件说明（附来源）

---

## 工作流 8：graph（知识图谱）

使用 **4-Signal Relevance 模型** 计算节点间相关性。

| 信号 | 权重 | 说明 |
|------|------|------|
| **Direct link** | ×3.0 | 页面通过 `[[wikilink]]` 直接互相引用 |
| **Source overlap** | ×4.0 | 两个页面的 `sources[]` 字段指向同一原始源文件（权重最高） |
| **Adamic-Adar** | ×1.5 | 两个页面有共同邻居节点，根据邻居的度数加权 |
| **Type affinity** | ×1.0 | 两个页面属于同一类型（entity/entity, topic/topic 等） |

### 步骤

1. **扫描双向链接**：遍历 `wiki/` 下所有 `.md` 文件，提取 `[[链接]]`

2. **计算 4-Signal 相关性**：
   - 提取所有页面的 YAML frontmatter（`type`, `sources[]` 字段）
   - 对每一对页面计算四个信号值并加权求和
   - 只保留相关性 ≥ 2.0 的边（避免图谱过于稠密）

3. **生成 Mermaid 图表** `wiki/knowledge-graph.md`：
   - 使用 `graph LR` 布局
   - 节点名截断到 10 字
   - 边的标签标注相关性分数（如 `[3.5]`）
   - 只展示相关性 ≥ 2.0 的节点
   - 关系超过 50 条时，只保留被引用最多的 30 个节点

4. **生成结构化数据** `wiki/graph-data.json`：
   ```json
   [
     {"nodes": [{"id": "A", "type": "entity|topic|source", "connections": 5}], ...},
     {"edges": [{"source": "A", "target": "B", "weight": 3.5, "signals": {"direct_link": 1, "source_overlap": 2, "adamic_adar": 0.5}}], ...}
   ]
   ```
   - 如果系统安装了 Node.js，生成交互式 HTML 图谱 `wiki/knowledge-graph.html`

5. **图谱洞察**（随图谱一起输出）：
   - **最关联对**：相关性分数最高的 3 对页面
   - **隐性关联**：无直接链接但 source_overlap ≥ 4.0 的页面（同源但未互链）
   - **孤立节点**：连接数 < 2 的页面（建议检查是否需要补充链接）
   - **知识空白**：引用最多的来源所关联的主题中，哪些实体还未建立

---

## 工作流 9：delete（删除素材）

### 步骤

1. **识别目标素材**：在 `raw/` 和 `wiki/sources/` 中定位
2. **扫描影响范围**：哪些实体页/主题页引用了该素材
3. **安全确认**：影响超过 5 个页面时，列出全部受影响文件让用户二次确认
4. **执行级联清理**：
   - 删除 raw 文件
   - 删除 sources 摘要页
   - 更新 entities 和 topics 中的引用（保留页面但移除该素材引用）
   - 如果实体/主题只被这个素材引用，询问用户是否一起删除
   - 更新 index.md 和 log.md
5. **清理缓存**：从 `.wiki-cache.json` 中移除对应条目
6. **断链检查**：确认没有遗留悬空引用

---

## 工作流 10：reviews（查看待审项）

用户说"查看待审"、"pending reviews"、"有没有需要我确认的"时触发。

### 步骤

1. **读取 `wiki/reviews/` 目录**，列出所有 `status: pending` 的 review 页面
2. **展示待审摘要**（标题 + 问题描述 + 预生成搜索词）
3. **询问用户**要处理哪个 review
4. **用户选择后**：
   - **create_page** → 按用户确认的内容创建新页面，更新 index.md 和 log.md
   - **deep_research** → 用预生成搜索词执行 WebSearch，消化新素材
   - **skip** → 标记为 `status: declined`
5. **更新 review 页面**的 `status` 字段
6. **全部处理后**：输出总结（"已处理 {N} 个待审项"）

---

## 工作流 11：crystallize（结晶化）

用户主动提供自己的思考、笔记、洞见（非外部素材）。

### 步骤

1. **提取核心洞见**（3-5 条）
2. **关键决策和原因**
3. **与现有知识库对比**，找出新增/修正的部分
4. **生成综合分析页面**保存到 `wiki/synthesis/sessions/{主题}-{日期}.md`
   - 内容默认标注 `confidence: INFERRED`
   - 参考 `templates/synthesis-template.md`
5. **更新 log.md**

---

## 文件格式规范

需要创建或更新 wiki 页面时，先读取 `references/file-format-spec.md` 获取 YAML frontmatter 标准、置信度标注规则及各页面类型格式。生成页面时结合 `templates/` 下对应模板。

---

