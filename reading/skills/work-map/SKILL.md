---
name: work-map
description: Map a book's core task, reader promise, architecture, concepts, reading focus, likely misreadings, and boundaries according to its reading mode. Use for the Work layer of a Reading Coach map while avoiding chapter-summary drift and claims beyond the available text.
---

# Work Map

回答：这本书本身到底提供了什么？把作品的任务和结构变得可见，不要退化为摘要。

## 通用流程

1. 用一个问题描述作者试图回答、展示或解决什么。
2. 说明读者可能获得的新经验、解释、方法或知识结构。
3. 按主次阅读模式分析作品架构：
   - `experience`：经验世界、叙述视角、人物处境、反复意象、语言质地、情绪结构。
   - `argument`：核心命题、概念关系、论证路径、前提、反对对象、结论边界。
   - `method`：使用场景、核心模型、步骤、示例、练习方式、适用范围。
   - `knowledge`：基础概念、领域结构、关键机制、前置知识、难点顺序、理论与实践。
4. 指出读者最可能采用的错误入口，并提供具体纠正。
5. 说明作品的适用边界。

## 范围约束

- `metadata_only`：不要生成 Work 分析；只说明当前缺少什么。
- `pre_reading`：只使用可靠目录、作者说明、出版社信息和权威评论。把待正文验证的判断写入 `uncertainty`。
- `text_grounded`：让结构、语言、意象或论证判断绑定到具体章节、页码或用户提供的段落。

只有目录不等于获得全文。不要根据书名、封面文案或常识虚构章节、意象、情节和论证。

## 输出契约

```yaml
work:
  core_question: string
  reader_promise: string
  central_thesis_or_experience: string
  architecture:
    - section: string
      function: string
  key_concepts:
    - concept: string
      plain_explanation: string
      relation_to_other_concepts: string
  reading_focus:
    - string
  likely_misreadings:
    - misunderstanding: string
      correction: string
  boundaries:
    - string
```

## 门禁

确认结果回答作品的核心任务、完成任务的结构、真正提供的价值和最可能的误读。若删除 Context 与 Author 后只剩普通简介，压缩摘要并重建阅读入口。
