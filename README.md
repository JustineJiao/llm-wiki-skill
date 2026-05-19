# llm-wiki — AI 驱动的个人知识库构建系统

> **把碎片化的信息变成持续积累、互相链接的知识库。你只需要提供素材，AI 做所有的整理工作。**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Platform: AI Agent](https://img.shields.io/badge/Platform-WorkBuddy-blue)]()
[![Version](https://img.shields.io/badge/version-3.7.0--wb1-green)]()
[![GitHub](https://img.shields.io/badge/GitHub-llm--wiki--skill-181717?logo=github)](https://github.com/sdyckjq-lab/llm-wiki-skill)

---

## 📖 概述

**llm-wiki** 是一个基于 AI Agent 方法论的个人知识库构建系统，受到 [Andrej Karpathy 的 llm-wiki 概念](https://github.com/karpathy/llm-wiki) 启发。

核心理念：**知识被编译一次，然后持续维护**，而不是每次重新推导。传统 RAG 系统每次查询都要重新处理原始文档，而 llm-wiki 让 AI 在 ingest 阶段就将信息转化为结构化的、互相链接的 wiki 页面，后续查询直接利用已编译的知识。

### 核心特性

- **素材自动消化** — 支持网页、PDF、公众号、推特、YouTube、本地文件等多种来源
- **Two-Step CoT 分析** — 结构化分析 → 页面生成，Token 优化的两阶段管道
- **双向链接** — 使用 `[[wikilink]]` 格式自动构建知识图谱
- **Obsidian 兼容** — 目录结构和文件格式原生支持 Obsidian 浏览
- **置信度标注** — 每个信息点标注 `EXTRACTED / INFERRED / AMBIGUOUS / UNVERIFIED`
- **人机协作** — Review Items 机制处理不确定性信息
- **4-Signal 知识图谱** — 基于多维相关性的智能图谱扩展
- **多知识库支持** — 可同时管理多个不同主题的知识库
- **双语支持** — 中文/English 知识库

---

## 🏗️ 知识库结构

初始化后的知识库目录结构：

```
知识库根目录/
├── raw/                          # 原始素材
│   ├── articles/                 # 网页文章
│   ├── tweets/                   # X/Twitter
│   ├── wechat/                   # 微信公众号
│   ├── xiaohongshu/              # 小红书
│   ├── zhihu/                    # 知乎
│   ├── pdfs/                     # PDF 文献
│   ├── clippings/                # Obsidian Clippings 笔记
│   ├── onenote笔记/
│   ├── local/                    # 本地文件
│   └── assets/                   # 图片等附件
├── wiki/                         # 编译后的知识
│   ├── entities/                 # 实体页（基因、人物、概念等）
│   ├── topics/                   # 主题页（跨实体汇总）
│   ├── sources/                  # 素材摘要页
│   ├── synthesis/                # 综合分析/深度报告
│   ├── comparisons/              # 对比分析
│   ├── queries/                  # 查询记录
│   └── reviews/                  # 待审项
├── purpose.md                    # 研究方向与目标
├── index.md                      # 索引
├── log.md                        # 操作日志
├── overview.md                   # 执行摘要
└── .wiki-schema.md               # 知识库配置文件
```

---

## 🚀 快速开始

### 环境要求

- WorkBuddy / 支持 AI Agent 的 Code IDE
- Python 3.8+（用于图片处理和文本提取）
- Node.js（可选，用于交互式知识图谱）
- Obsidian（推荐，用于浏览知识库）

### 安装

1. 将此 skill 目录放置到 WorkBuddy 的 skills 目录中
2. 在 WorkBuddy 中加载 llm-wiki skill
3. 说 **"帮我初始化一个知识库"** 开始使用

### 基本用法

| 你想做什么 | 怎么说 |
|-----------|--------|
| 新建知识库 | "帮我初始化一个知识库" |
| 添加一篇网页 | 粘贴 URL，说"帮我消化这篇" |
| 添加一篇 PDF | 给文件路径，说"消化这个 PDF" |
| 批量添加 | "批量消化 D:\文献\这个文件夹" |
| 查询知识 | "关于 XX 是什么？" |
| 深度综述 | "给我讲讲 XX 的研究进展" |
| 健康检查 | "检查知识库" |
| 查看状态 | "知识库现在有什么" |

---

## 📋 工作流一览

| 工作流 | 用途 | 说明 |
|--------|------|------|
| **init** | 初始化知识库 | 创建目录结构、配置文件 |
| **ingest** | 消化单个素材 | 核心流程，AI 驱动 |
| **batch-ingest** | 批量消化 | 每 5 个暂停 + 批量交叉综合 |
| **query** | 查询知识 | 4 阶段混合搜索管线 |
| **lint** | 健康检查 | 断链/孤立/一致性检查 |
| **status** | 查看状态 | 统计 + 最近活动 |
| **digest** | 深度综合 | 跨素材深度报告 |
| **graph** | 知识图谱 | 4-Signal 相关性图谱 |
| **delete** | 删除素材 | 级联清理 |
| **reviews** | 查看待审 | 处理不确定性信息 |
| **crystallize** | 结晶化 | 用户思考沉淀 |

详情见 [docs/WORKFLOWS.md](docs/WORKFLOWS.md)

---

## 🔬 技术架构

### Two-Step CoT（核心 Token 优化）

```
Step 1（分析阶段）：读取 原素材全文 + 现有 wiki → 产出 结构化分析 JSON
Step 2（生成阶段）：读取 Step 1 分析 JSON + 相关已有页面（部分读取）→ 产出 wiki 页面
                         ^^^ 不重复读取原素材全文（关键节省）
```

### 4-Signal Relevance 模型

| 信号 | 权重 | 说明 |
|------|------|------|
| **Direct link** | ×3.0 | `[[wikilink]]` 直接互相引用 |
| **Source overlap** | ×4.0 | 共享同一原始源文件（最高权重） |
| **Adamic-Adar** | ×1.5 | 共同邻居节点加权 |
| **Type affinity** | ×1.0 | 同类型页面 |

### 置信度系统

| 标注 | 含义 | 证据要求 |
|------|------|---------|
| `EXTRACTED` | 原文直接陈述 | 必须，≤50字原文摘录 |
| `INFERRED` | 从多处原文推断 | 必须，说明推理依据 |
| `AMBIGUOUS` | 原文表述不清 | 可选 |
| `UNVERIFIED` | 来自 AI 背景知识 | 可选 |


---

## 📚 引用的来源与灵感

llm-wiki 的设计参考了以下项目和方法论：

### 核心灵感
1. **[sdyckjq-lab/llm-wiki-skill](https://github.com/sdyckjq-lab/llm-wiki-skill)** — 本项目的 GitHub 仓库
2. **[nashsu/llm_wiki](https://github.com/nashsu/llm_wiki)** — 基于 Karpathy 方法论的 llm-wiki 实现，本项目的工作流设计和 Two-Step CoT 分析管线受其启发
3. **[Karpathy's llm-wiki](https://github.com/karpathy/llm-wiki)** — 核心理念和方法论
   - "知识被编译一次，持续维护" 的概念
   - 目录结构灵感（entities/topics/sources）
   - 双向链接和 wiki 语法
4. **[Obsidian](https://obsidian.md/)** — 文件格式标准
   - YAML frontmatter 规范
   - `[[wikilink]]` 双向链接语法
   - 附件管理方式

### 方法借鉴
3. **Two-Step Chain-of-Thought** — Token 优化策略
   - Step 1（分析）和 Step 2（生成）分离
   - 分析 JSON 作为中间表示，减少 Step 2 上下文

4. **4-Signal Relevance Model** — 复合相关性计算
   - 参考推荐系统中的多信号融合排序
   - Adamic-Adar 指标来自社交网络分析

5. **混合搜索管线** — 搜索策略
   - 关键词搜索 + 图谱扩展 + 预算控制
   - 借鉴搜索引擎的倒排索引 + PageRank 模式

### 工具依赖
6. **[baoyu-url-to-markdown](https://github.com/sdyckjq-lab/baoyu-url-to-markdown)** — URL 转 Markdown 工具
7. **[markitdown](https://github.com/microsoft/markitdown)** — PDF/DOCX 转 Markdown
8. **[WorkBuddy](https://www.codebuddy.cn/docs/workbuddy/Overview)** — AI Agent 运行平台

---

## 🤝 贡献

欢迎通过 Issue 和 Pull Request 贡献。
- 报告 Bug：请附带完整的运行日志
- 功能建议：请说明使用场景和预期行为
- 代码贡献：请遵循现有的 YAML frontmatter 标准

---

## 📄 许可

[MIT License](LICENSE) © 2026 sdyckjq-lab
[GLP3.0 License](LICENSE) © 2026 nashsu
