# 工作流详细文档

本文档描述了 llm-wiki 的 11 个工作流的详细步骤。

---

## 1. init — 初始化知识库

创建新知识库的目录结构和配置文件。

**步骤**:
1. 询问知识库主题、语言、保存位置
2. 创建目录结构：raw/ 子目录 + wiki/ 子目录
3. 创建 `.wiki-schema.md`（主题、语言、别名词表）
4. 创建 `purpose.md`（研究目标）
5. 创建 `index.md`、`log.md`、`overview.md`
6. 将路径写入 `~/.llm-wiki-path`
7. 输出引导说明

**输出目录结构**:
```
知识库根目录/
├── raw/        ├── wiki/        ├── purpose.md
│   ├── articles│   ├── entities│ ├── index.md
│   ├── tweets   │   ├── topics  ├── log.md
│   ├── wechat   │   ├── sources ├── overview.md
│   ├── ...      │   ├── ...     └── .wiki-schema.md
│   └── assets   └── └── reviews
```

---

## 2. ingest — 消化单个素材

核心工作流，将一个原始素材转换为结构化的 wiki 页面。

### 素材类型路由

| 类型 | 工具 | 回退 |
|------|------|------|
| 网页 URL | WebFetch | — |
| X/Twitter | baoyu-url-to-markdown | WebSearch |
| 公众号 | wechat-article-search | WebSearch |
| YouTube | baoyu-url-to-markdown | 手动提示 |
| PDF | markdown-converter | Read 直接读 |
| DOCX/PPTX | markdown-converter | — |
| 本地 MD/TXT | Read | — |

### 完整处理流程（>1000 字）

1. **提取素材** → 2. **保存 raw 文件** → 3. **读取上下文** → 4. **SHA256 缓存检查**
5. **Step 1 分析**（JSON 结构化分析）
6. **Step 2 生成**（创建/更新 wiki 页面）
7. 生成 source 页 → 更新/创建 entity 页 → 更新/创建 topic 页
8. 更新 index.md → 更新 log.md → 输出结果

### 简化处理流程（≤1000 字）

跳过 Step 1 的分析 JSON，直接生成简化摘要页（不写"原文精彩摘录"），只提取 1-3 个关键概念。

---

## 3. batch-ingest — 批量消化

**步骤**: 确认路径 → 列出文件 → 用户确认 → 逐个处理（带缓存检查） → 每 5 个暂停 → 完成后 Batch 交叉综合

### Batch 交叉综合

批量消化后在所有新页面之间建立关联：
1. 在实体页的"相关实体"中补充 batch 内互链
2. 创建/更新主题页汇总本 batch 素材
3. 更新 index.md 关联关系
4. 记录到 log.md

---

## 4. query — 查询知识

4 阶段混合搜索管线：

**Phase 1**: 关键词搜索（别名展开 → 标题加权 + 正文命中 → Top 10）
**Phase 2**: 图谱扩展（种子节点 → 4-Signal 计算 → 2-hop 遍历 → Top 8）
**Phase 3**: 预算控制（按可用 Token 裁剪低分页面）
**Phase 4**: 上下文组装（差异读取 → 综合回答 → 出处标注）

---

## 5. lint — 健康检查

检查范围：最近 10 个页面 + 随机 10 个

机械检查：
- 孤立页面（未被引用的实体）
- 断链（[[X]] 但 X.md 不存在）
- index 一致性（有记录无文件 / 有文件无记录）

AI 判断：
- 矛盾信息（同一实体不同页面冲突）
- 交叉引用缺失
- 置信度分布报告

---

## 6. status — 查看状态

统计 raw/ 各子目录文件数、wiki/ 各子目录页面数、最近 5 条 log 记录。

---

## 7. digest — 深度综合报告

区别于 query（快速问答）：digest 生成持久化的综合分析页面。

输出格式：
- 对比 → 对比表格式
- 时间线 → Mermaid gantt + 事件说明
- 其他 → 深度报告格式

---

## 8. graph — 知识图谱

1. 扫描所有 `[[wikilink]]`
2. 计算 4-Signal 相关性（Direct link ×3.0 / Source overlap ×4.0 / Adamic-Adar ×1.5 / Type affinity ×1.0）
3. 生成 Mermaid 图表
4. 生成 graph-data.json
5. 可选：生成交互式 HTML 图谱

---

## 9. delete — 删除素材

级联清理：删除 raw 文件 → 删除 source 页 → 更新 entity/topic 引用 → 更新 index/log → 清理缓存 → 断链检查

---

## 10. reviews — 查看待审项

列出 wiki/reviews/ 中 status: pending 的 review 页面，用户确认后执行创建/研究/跳过操作。

---

## 11. crystallize — 结晶化

将用户自己的思考、笔记、洞见沉淀到知识库：
1. 提取核心洞见（3-5 条）
2. 与现有知识对比
3. 生成综合分析页面（confidence: INFERRED）
4. 更新 log.md
