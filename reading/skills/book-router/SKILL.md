---
name: book-router
description: Choose a book's primary and optional secondary reading mode, state its reader promise, and allocate context-author-work analysis weights. Use after book identity is confirmed or when a Reading Coach analysis needs depth and mode decisions.
---

# Book Router

判断作品主要向读者提供什么，而不是只贴“文学”“管理”或“技术”等类别标签。

## 阅读模式

- `experience`：提供经验、情绪、人物世界或生命感受。
- `argument`：提出概念、判断和论证。
- `method`：帮助读者完成任务或改善能力。
- `knowledge`：建立专业领域的知识结构。

允许一个主模式和一个不同的次模式。

## 流程

1. 阅读已确认的 `identity`、用户目标和可用作品资料。
2. 用一句话说明作者希望读者获得什么。
3. 选择主模式；只有第二种模式会显著改变分析方法时才选择次模式。
4. 分配 Context、Author、Work 权重。三项总和必须等于 100，任何一项都不得为 0。
5. 说明最重要的一层、应简写的一层及理由。
6. 给出路由置信度；低于 `0.75` 时说明导致不确定的材料。

## 建议基线

```yaml
experience: {context: 35, author: 30, work: 35}
argument: {context: 20, author: 15, work: 65}
method: {context: 10, author: 10, work: 80}
knowledge: {context: 15, author: 5, work: 80}
```

根据具体作品调整，不要机械复制基线。

## 输出契约

```yaml
routing:
  primary_mode: experience | argument | method | knowledge
  secondary_mode: experience | argument | method | knowledge | null
  reader_promise: string
  context_weight: integer
  author_weight: integer
  work_weight: integer
  routing_reason: string
  confidence: number
```

## 门禁

确保 `context_weight + author_weight + work_weight = 100`。确保 `routing_reason` 回答：为什么是这个模式、哪层最重要、哪层简写。只输出类别名视为失败。
