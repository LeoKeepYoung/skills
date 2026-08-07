# Quality Gates

在渲染最终 Markdown 前按顺序执行全部门禁。记录每个门禁的 `pass` 或 `fail`；任何失败都使最终 `quality.status` 为 `blocked`。

## Gate 0：身份

检查书名、作者、原文名、版本、作品形式和分析范围是否互相一致。

通过条件：

- `identification_confidence >= 0.8`；
- 没有会显著改变作品内容的未决版本歧义；
- 输入不是被误认成书籍的章节、文章或系列。

失败时停止后续分析，并返回候选项和确认问题。

## Gate 1：路由

检查阅读模式、读者承诺和三层权重。

通过条件：

- `routing.confidence >= 0.75`；
- 主模式有充分理由；
- 三项权重总和为 100 且均大于 0；
- 主次模式不重复；
- 没有用错误模式主导分析。

## Gate 2：证据

检查关键身份、生平、时代和作品主张是否可追踪，推断是否明确标记，来源是否冲突。

通过条件：

- 关键事实存在对应 Evidence；
- `system_inference` 没有伪装成事实；
- 未确认内容进入 `uncertainty`；
- 来源冲突已并列呈现。

## Gate 3：因果链

检查：

```text
Context → Author
Author → Work
Context → Work
```

每条连接必须说明中间机制。只把两个事实用“所以”连接不算通过。

## Gate 4：过度解释

检查是否：

- 用单一经历解释作者全部创作；
- 远距离诊断作者人格；
- 把一个意象固定为唯一含义；
- 把时代背景作为万能解释；
- 把作者等同于叙述者。

发现问题时降低措辞强度、补充替代解释或删除断言。

## Gate 5：摘要漂移

判断：

> 删除时代和作者信息后，结果是否仍然只是普通书籍简介或章节摘要？

如果是，压缩复述，强化作品任务、阅读重点、误读与边界。

## Gate 6：阅读价值

至少提供：

- 一个明确阅读重点；
- 一个容易误读点及纠正；
- 一个阅读中的观察问题；
- 一个迁移边界。

建议必须具体到本书，不能只说“认真阅读、做好笔记”。

## Gate 7：完整性

确认存在：

```yaml
- identity
- routing
- context
- author
- work
- entry
- evidence
- uncertainty
- quality
```

允许低权重层较短，但不得无故省略。资料不足时明确写出限制。

## Quality 记录

```yaml
quality:
  status: pass | blocked
  gates:
    gate_0_identity: pass | fail
    gate_1_routing: pass | fail
    gate_2_evidence: pass | fail
    gate_3_causal_links: pass | fail
    gate_4_overinterpretation: pass | fail
    gate_5_summary_drift: pass | fail
    gate_6_reading_value: pass | fail
    gate_7_completeness: pass | fail
  notes:
    - string
```

只有全部门禁为 `pass` 时，`quality.status` 才能为 `pass`。
