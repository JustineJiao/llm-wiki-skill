# SOURCES.md — 引用来源与灵感

## 本文档

本文档列出了 llm-wiki 设计过程中引用的所有来源、项目、论文和方法论。按影响程度排序。

---

## 🔥 核心来源（直接影响设计决策）

### 1. sdyckjq-lab/llm-wiki-skill

- **来源**: https://github.com/sdyckjq-lab/llm-wiki-skill
- **说明**: 本项目的 GitHub 仓库，WorkBuddy 平台上的 llm-wiki Skill 实现
- **贡献**: 本包即该仓库的代码

### 2. nashsu/llm_wiki

- **来源**: https://github.com/nashsu/llm_wiki
- **作者**: nashsu
- **影响程度**: 核心参考实现
- **贡献**:
  - 基于 Karpathy 方法论的完整 llm-wiki 实现
  - 工作流设计（ingest/query/digest 管线）的主要参考来源
  - Two-Step CoT 分析管线的设计启发
  - 结构化分析 JSON 格式的设计参考
  - Review Items 机制的灵感来源

### 3. Karpathy's llm-wiki

- **来源**: https://github.com/karpathy/llm-wiki
- **作者**: Andrej Karpathy
- **影响程度**: 核心理念和方法论
- **贡献**:
  - "知识被编译一次，持续维护" 的核心概念
  - 目录结构设计灵感（entities/ → topics/ → sources/ 架构）
  - 双向链接和 wiki 风格的页面组织方式
  - 素材消化后生成持久化页面的管线思想
  - 知识图谱和索引维护机制
- **差异**:
  - Karpathy 原版使用 Python 工具链（CLI + 本地 LLM）
  - 本版完全基于 AI Agent（无外部工具依赖）
  - 新增 Two-Step CoT、4-Signal 模型、Review Items 等

### 2. Obsidian

- **来源**: https://obsidian.md/
- **作者**: Obsidian 团队
- **影响程度**: 文件格式标准
- **贡献**:
  - YAML frontmatter 作为页面元数据标准
  - `[[wikilink]]` 双向链接语法
  - `attachments/` 附件管理规范
  - 知识图谱（graph view）概念整合
  - 标签系统和搜索机制

---

## ⚡ 方法论借鉴

### 3. Chain-of-Thought Prompting

- **来源**: Wei et al. (2022), "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
- **作者**: Jason Wei, Xuezhi Wang, Dale Schuurmans et al. (Google)
- **影响**: llm-wiki 的 **Two-Step CoT** 管道设计
- **具体**:
  - Step 1（分析）：将源素材分解为结构化分析 JSON
  - Step 2（生成）：基于分析结果生成页面
  - 分离分析和生成阶段以优化 Token 使用

### 4. Retrieval-Augmented Generation (RAG)

- **来源**: Lewis et al. (2020), "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
- **作者**: Patrick Lewis, Ethan Perez, Aleksandra Piktus et al. (Facebook AI)
- **影响**: llm-wiki 的 query 工作流
- **差异**: RAG 每次查询重新检索；llm-wiki 编译知识到 wiki 页面后持久化

### 5. Adamic-Adar 指标

- **来源**: Adamic & Adar (2003), "Friends and neighbors on the Web"
- **影响**: 4-Signal Relevance 模型中的社会网络分析指标
- **公式**: 共同邻居的度数倒数之和

### 6. 倒排索引 + PageRank

- **来源**: 经典信息检索 + Brin & Page (1998)
- **影响**: 混合搜索管线中的关键词搜索 → 图谱扩展架构

---

## 🛠️ 工具依赖

### 7. baoyu-url-to-markdown

- **来源**: 内部项目
- **用途**: URL 转 Markdown（CDP 抓取 + 站点适配器）
- **使用场景**: 微信公众号、推特、YouTube 等来源提取

### 8. Microsoft markitdown

- **来源**: https://github.com/microsoft/markitdown
- **用途**: PDF、DOCX、PPTX 等文件转 Markdown
- **使用场景**: PDF 文献消化、本地文件转换

### 9. WorkBuddy

- **来源**: https://www.codebuddy.cn/docs/workbuddy/Overview
- **用途**: AI Agent 运行平台
- **使用场景**: 所有 AI 分析操作的执行环境

---

## 📚 参考论文

### 知识管理
- Ackerman, M. S. (2000). "The Intellectual Challenge of CSCW: The Gap Between Social Requirements and Technical Feasibility in Groupware."
- Nonaka, I. & Takeuchi, H. (1995). "The Knowledge-Creating Company."

### 个人知识管理工具
- Roam Research (https://roamresearch.com/) — 双向链接的现代推广者
- Notion (https://www.notion.so/) — 数据库驱动的知识管理
- Logseq (https://logseq.com/) — 开源的双向链接知识库

### AI 辅助知识管理
- Nakajima, Y. (2025). "llm-answer-tools" — 知识库搜索工具设计参考
- GitHub Models / Claude Code skills — Skills 驱动的 AI 工作流

---

## 📝 版本说明

| 版本 | 日期 | 主要变化 |
|------|------|---------|
| 3.7.0-wb1 | 2026-05 | 适配 WorkBuddy，Two-Step CoT，Review Items |
| 3.6.0-wb1 | 2026-04 | 初始 WorkBuddy 适配 |
| v1 (Karpathy) | 2024 | 原始概念版 |
