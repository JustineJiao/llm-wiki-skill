# Batch 交叉综合

> 仅供 `batch-ingest` 工作流引用。在批量消化所有文件完成后执行一次。

## 步骤

1. **逐个 ingest 所有文件**（按 [Token 优化策略](token-optimization.md) 的 Two-Step CoT 流程）

2. **批量交叉综合**（所有文件消化完后，额外一次调用）：
   - **输入**：本次 batch 中所有新创建的 source 页面 + 新创建的 entity 页面
   - **输出**：文件间的交叉关联 → 更新已创建的实体页、创建新的 cross-reference 连接
   - **具体产出**：
     - 在实体页的"相关实体"中补充 batch 文件间的互链
     - 创建/更新主题页，汇总本 batch 相关素材
     - 更新 index.md 中的关联关系

3. **集成到 log.md**：记录 batch 批次的交叉发现
   - 格式：`## {日期} batch-cross-synthesis | {N} 个文件`
