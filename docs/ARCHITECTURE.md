# 系统架构

## 整体架构

```
用户输入 (URL/文件/文本/命令)
        │
        ▼
┌─────────────────────────────────────────┐
│            WorkBuddy AI Agent            │
│  (Read/Write/Edit/WebFetch/Search 等)   │
└──────────────┬──────────────────────────┘
               │
     ┌─────────┴─────────┐
     │                   │
     ▼                   ▼
┌──────────┐    ┌──────────────┐
│  Raw 素材 │    │   wiki 知识   │
│ (raw/)   │◄──►│ (wiki/)      │
└──────────┘    └──────────────┘
                      │
               ┌──────┴──────┐
               │             │
               ▼             ▼
        ┌──────────┐  ┌──────────┐
        │ index.md │  │ .wiki-   │
        │ log.md   │  │ schema   │
        │ purpose  │  │ cache    │
        └──────────┘  └──────────┘
```

## 核心组件

### 1. 素材层 (raw/)

存储未经修改的原始素材。按来源类型分目录存放：
- `articles/` — 网页文章
- `tweets/` — X/Twitter
- `wechat/` — 微信公众号
- `pdfs/` — PDF 文献
- `clippings/` — Obsidian Clippings 笔记
- `local/` — 本地文件
- `assets/` — 图片附件

### 2. 知识层 (wiki/)

存储经过 AI 编译的结构化知识：
- **entities/** — 实体页（基因、人物、概念等原子知识单元）
- **topics/** — 主题页（跨实体的主题汇总）
- **sources/** — 素材摘要页（每个原始素材对应一页）
- **synthesis/** — 综合分析/深度报告
- **comparisons/** — 对比分析
- **queries/** — 查询记录
- **reviews/** — 待审项

### 3. 元数据层

- **index.md** — 全库索引
- **log.md** — 操作日志
- **purpose.md** — 研究方向和目标
- **.wiki-schema.md** — 配置文件
- **.wiki-cache.json** — SHA256 缓存

## Token 优化架构

### Two-Step CoT 管道

```
Step 1 (分析阶段)
  输入: 素材全文 (40%) + wiki上下文 (30%) + 指令 (10%) → 分析JSON (20%)
  输出: {"source_summary", "entities", "topics", "connections", ...}
  
Step 2 (生成阶段) 
  输入: 分析JSON (40%) + 已有页面部分读取 (40%) + 指令 (20%)
  输出: source页 + entity页 + topic页 + review items
  ※ 不读取素材全文！—— 关键Token节省
```

### 页面部分读取规则

- 已有页面只读前 500 字 + YAML frontmatter
- 超过 2000 字的页面用 grep 定位相关段落
- 不读取 overview.md、log.md、index.md 正文

## 混合搜索管线 (4-Phase)

```
Phase 1: 关键词搜索 → 别名展开 → 标题/正文匹配 → Top 10
Phase 2: 图谱扩展 → 4-Signal 模型 → 2-hop 遍历 → Top 8
Phase 3: 预算控制 → Token 配额 → 裁剪低分页面
Phase 4: 上下文组装 → 差异读取 → 综合回答
```

## 4-Signal Relevance 模型

```
Score(A, B) = 3.0 × direct_link + 4.0 × source_overlap + 1.5 × adamic_adar + 1.0 × type_affinity
```

其中：
- `direct_link` = 1 如果 [[A]] 引用 B 或 [[B]] 引用 A
- `source_overlap` = A 和 B 共享的 sources[] 数量
- `adamic_adar` = Σ(1/log(degree(n))) for n in neighbors(A) ∩ neighbors(B)
- `type_affinity` = 1 如果 type(A) == type(B)
