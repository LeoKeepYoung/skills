# 证据政策

## 目标

让读者看出哪些内容可核验、哪些属于解释、哪些仍未知。证据的作用不是装饰文章，而是控制结论强度。

## 主张类型

| 类型 | 定义 | 写法 |
|---|---|---|
| `fact` | 可由可靠来源核验的事实 | 直接陈述并给出来源 |
| `accepted_interpretation` | 学术界、评论界或作者研究中较常见的解释 | 说明“常被理解为”并给出代表来源 |
| `system_inference` | 根据已知事实建立的分析性连接 | 使用“可能、提示、可以理解为”，列出依据 |
| `open_question` | 当前资料不足或来源冲突 | 明确问题和它对分析的影响 |

不要把 `accepted_interpretation` 当作共识，除非来源确实显示高度一致。

## 来源优先级

按主张类型选择最接近原始事实的来源：

1. 作者原文、访谈、书信、演讲、官方档案；
2. 出版社书目页、版权页、国家图书馆或大学图书馆目录；
3. 同行评审论文、学术专著、大学或研究机构资料；
4. 有编辑审校与署名的高质量评论；
5. 其他二手资料，仅用于发现线索，不作为关键事实的唯一依据。

不要把搜索结果摘要、无署名聚合页、营销文案或模型记忆当作最终证据。

## 最低核验要求

- 对书籍身份、作者、原文名、首次出版时间和版本差异，优先使用书目或出版社来源。
- 对会改变核心分析的时代事实和作者生平事实，至少寻找两个相互独立的可靠来源；找不到时降低结论强度。
- 对作者动机，优先寻找作者明确陈述；没有直接陈述时标记为解释或推断。
- 对作品结构，使用目录、正文或可靠版本说明；只有简介时不要声称掌握章节结构。
- 对具体文本、意象和语言判断，必须有可定位文本。

## Evidence 记录

每个关键主张使用：

```yaml
- claim_id: E1
  claim: string
  claim_type: fact | accepted_interpretation | system_inference | open_question
  section: identity | context | author | work | entry
  source_title: string | null
  source_url: string | null
  locator: string | null
  source_quality: primary | authoritative | scholarly | editorial | other | none
  supports:
    - string
```

`system_inference` 仍应在 `supports` 中指向所依据的事实；`open_question` 可以没有来源，但应写明缺口。

## 冲突与不确定性

来源冲突时：

1. 并列记录各说法及来源；
2. 说明冲突影响的是身份、时间、解释还是细节；
3. 不要选择更戏剧化的说法；
4. 身份或版本冲突足以改变分析时停止；
5. 其他冲突进入 `uncertainty`。

不确定性使用：

```yaml
- issue: string
  impact: string
  action: string
```

## 语言强度

发现过度解释时按以下方向降级：

```text
导致 → 可能影响
证明 → 提示
就是 → 可以理解为
必然 → 在这些材料下更可能
作者想要 → 作者明确表示 / 可以推断
```

正文中的自然语言必须与 Evidence 记录的主张类型一致。
