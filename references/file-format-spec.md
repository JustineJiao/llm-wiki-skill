# 文件格式规范

> 引用此文档时仅需查阅所需页面类型的 YAML frontmatter 和格式要求。
> 生成页面时，先读取 `templates/` 下对应模板，再按本文档填充 frontmatter。

## YAML Frontmatter 统一标准

所有 `wiki/` 下的页面**必须包含**标准化 YAML frontmatter：

```yaml
---
type: source | entity | topic | query | synthesis | comparison
title: <页面标题>
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: []            # 引用来源列表（raw 文件路径）
tags: []               # 标签
aliases: []            # 别名，用于 [[wikilink]] 匹配
confidence: EXTRACTED | INFERRED | AMBIGUOUS | UNVERIFIED
---
```

各页面类型特有字段见对应模板文件。

### YAML Frontmatter 的作用

- **机器可读**：支持自动索引、图谱生成、搜索排序
- **源追溯**：每个页面知道自己信息来源，查询时提供出处
- **级联维护**：删除素材时通过 `sources` 字段定位受影响页面
- **Obsidian 兼容**：YAML frontmatter + `[[wikilinks]]` 是 Obsidian 原生格式

## 置信度标注规则

| 标注 | 含义 | evidence 要求 |
|------|------|--------------|
| `EXTRACTED` | 原文直接陈述 | 必须，≤50字原文摘录 |
| `INFERRED` | 从多处原文推断 | 必须，说明推理依据 |
| `AMBIGUOUS` | 原文表述不清 | 可选 |
| `UNVERIFIED` | 来自AI背景知识 | 可选 |

## 页面类型格式

### 素材摘要页（wiki/sources/）
参考 `{SKILL_DIR}/templates/source-template.md`

### 实体页（wiki/entities/）
参考 `{SKILL_DIR}/templates/entity-template.md`

### 主题页（wiki/topics/）
参考 `{SKILL_DIR}/templates/topic-template.md`

## index.md 格式

```markdown
# 知识库索引

## 实体（N）
- [[实体1]] — 简短描述

## 主题（N）
- [[主题1]] — 简短描述

## 素材（N）
- [[素材1]] — 来源类型，日期

## 综合分析（N）
- [[分析1]] — 日期
```
