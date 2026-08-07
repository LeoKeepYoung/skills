---
name: reading-entry
description: Integrate confirmed Context, Author, Work, and routing results into a concrete pre-reading orientation, attention strategy, questions, and transfer boundary. Use after the three analysis layers are complete; do not use it to introduce new facts.
---

# Reading Entry

把已有分析变成读者打开第一页之前真正可用的入口。只整合，不新增事实。

## 输入

接收 `identity`、`routing`、`context`、`author`、`work`、`evidence` 与 `uncertainty`。

## 流程

1. 压缩一条可解释的核心链：

   ```text
   什么样的世界 → 塑造什么样的作者视角 → 产生什么样的作品
   ```

2. 按阅读模式给出具体阅读姿势：
   - 文学体验：先观察经验、形式与语言，不要急于找唯一论点。
   - 思想论证：追踪概念前提、论证路径与边界。
   - 方法工具：边读边练，区分模型、场景与限制。
   - 专业知识：先建立概念依赖与前置知识。
3. 生成能改变注意力的阅读问题，不要生成考试题。
4. 说明可以迁移的视角与不应套用的方式。
5. 从不确定性中挑出会影响阅读姿势的事项，明确提醒读者。

## 输出契约

```yaml
entry:
  one_sentence_positioning: string
  context_author_work_chain: string
  before_reading:
    - string
  while_reading:
    - string
  do_not_force:
    - string
  stop_and_think_questions:
    - string
  transfer_boundary:
    useful_insight: string
    misuse_risk: string
```

## 门禁

确保结果至少包含一个明确阅读重点、一个具体误读提醒、一个观察问题和一个迁移边界。删除“认真阅读、做好笔记、体会思想”等对任何书都成立的空泛建议。
