---
name: context-analysis
description: Analyze the historical, social, cultural, industry, academic, or technical world relevant to a book and connect it to human stakes and the work's necessity. Use for the Context layer of a Reading Coach map, not for a general history overview.
---

# Context Analysis

回答：这本书面对怎样的世界，那个世界为什么需要这本书？

## 流程

1. 按 `routing.context_weight` 控制篇幅，只选择真正影响本书的问题。
2. 确认相关时间、地点及社会、文化、行业、学术、技术或观念环境。
3. 识别一至三个核心张力，例如“复杂信息 ↔ 沟通能力”。
4. 把环境落实到当时普通人的经验、工作或思想处境。
5. 建立至少一条完整链路：

   ```text
   环境事实 → 人的处境 → 作者面对的问题 → 作品出现的必要性
   ```

6. 标记每个关键主张的证据类型与来源。避免用今天的价值判断替代当时语境。

## 输出契约

```yaml
context:
  period_and_place: string
  relevant_environment:
    - string
  central_tensions:
    - side_a: string
      side_b: string
      explanation: string
  impact_on_people:
    - string
  bridge_to_book:
    - string
  required_prior_knowledge:
    - string
  context_importance: essential | helpful | optional
```

## 门禁

确认至少一条环境事实能够通过人的处境连接到作者问题和作品。删除不能回答“这为何有助于理解本书”的资料。

## 禁止

不要写通史，不要堆年代与事件，不要把所有内容归因于时代，不要用单一宏大叙事覆盖地区、阶层或群体差异。
