---
name: author-lens
description: Extract only the author experiences, recurring questions, observation methods, and expression styles that illuminate a specific work. Use for the Author layer of a Reading Coach map or when explaining why this person wrote this work in this way without producing a full biography.
---

# Author Lens

提炼作者与本书相关的观察视角。不要撰写完整传记。

## 流程

1. 按 `routing.author_weight` 控制深度，只保留能够帮助理解本书的经历。
2. 识别作者在多部作品、访谈或生涯中反复追问的问题。
3. 识别作者的观察与表达方法，如逻辑分析、临床观察、历史比较、案例归纳、诗性隐喻或第一人称经验。
4. 为每项经历建立：

   ```text
   经历 → 长期问题 → 观察方式 → 本书形式或主题
   ```

5. 明确区分可核验事实、常见解释与系统推断。降低无法直接证明的因果措辞强度。
6. 记录作者层资料的局限。

## 输出契约

```yaml
author:
  relevant_life_events:
    - event: string
      relevance_to_book: string
      evidence_level: fact | accepted_interpretation | system_inference
  recurring_questions:
    - string
  author_lens:
    - string
  thinking_and_expression_style:
    - string
  links_to_work:
    - from: string
      to: string
      relation: string
  limitations:
    - string
```

## 门禁

每条人生经历必须说明与本书的关系。资料不足时缩短本层，并写明“不对作者动机作推断”。

## 禁止

不要远距离诊断人格，不要用单一经历解释全部创作，不要把作者等同于叙述者，不要把合理推断写成作者明确承认的动机，不要输出出生、毕业、获奖、逝世式流水账。
