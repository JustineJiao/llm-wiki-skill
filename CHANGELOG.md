# CHANGELOG

## 3.7.0-wb1 (2026-05-19)
- 仓库: https://github.com/sdyckjq-lab/llm-wiki-skill
- 许可证: GPL-3.0
- 适配 WorkBuddy 平台，去除外部 CLI/API 依赖
- 所有操作通过 WorkBuddy 原生工具（Read/Write/Edit/Grep/Glob）实现
- 新增 Token 优化策略：Two-Step CoT + 页面部分读取
- 新增 4-Signal Relevance 模型用于图谱扩展和混合搜索
- 新增 Review Items 机制（人机协作)
- 新增 Batch 交叉综合（批量消化后的文件间关联发现）
- 新增 `crystallize` 工作流（用户思考/笔记结晶化）
- 新增 `reviews` 工作流（待审项管理）
- 更新 YAML frontmatter 统一标准
- 支持中/英双语知识库
- 优化 query 工作流为 4 阶段混合搜索管线

## 3.6.0-wb1 (2026-04-xx)
- 初始 WorkBuddy 适配版本
- 核心工作流：init / ingest / batch-ingest / query / lint / status / digest / graph / delete

## 原始版本（Karpathy 方法论）
- 基于 https://github.com/karpathy/llm-wiki 的概念和目录结构
- 移除了原始 Python 工具链，重写为 AI Agent 驱动
