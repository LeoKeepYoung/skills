---
name: reading
description: Orchestrate a book through pre-reading research, active-reading tracking and discussion, and post-reading reflection in one evidence-aware Obsidian note. Use when a user asks to prepare for a book, start or continue reading, sync WeRead progress, discuss a reading question, review notes after finishing, choose personalized output topics, or request follow-up books.
---

# Reading

将一本书的阅读过程路由到读前、读中、读后三个阶段，并让三个阶段共享同一份书籍身份与 Obsidian 笔记。不要把三个阶段一次性跑完。

## 先读取共同协议

执行任何阶段前读取：

- [生命周期协议](references/lifecycle-contract.md)
- [证据政策](references/evidence-policy.md)

需要写入 Obsidian 时再读取 [书籍笔记模板](templates/book-reading.md)。

## 识别当前阶段

按用户的明确意图和已存在状态路由：

| 用户状态或请求 | 阶段 | 执行的 Skill |
|---|---|---|
| 尚未决定阅读；询问值不值得读、作者、背景或怎么读 | 读前 | [Prepare Reading](skills/prepare-reading/SKILL.md) |
| 已经在读/读完，但明确要求补做读前分析 | 读前（回溯式） | [Prepare Reading](skills/prepare-reading/SKILL.md)，完成后回到实际阶段 |
| 明确表示开始/正在阅读；要求建档、同步进度或讨论困惑 | 读中 | [Continue Reading](skills/continue-reading/SKILL.md) |
| 微信读书精确进度为 100%，或用户明确确认已经读完 | 读后 | [Complete Reading](skills/complete-reading/SKILL.md) |

一次只读取并执行命中阶段的 Skill。阶段不明时优先从读前开始；不要仅凭书架状态、最近阅读时间或笔记数量推定已经开始或读完。

## 状态转换

只允许以下转换：

```text
planned --用户确认开始阅读且确认 Obsidian 目录--> reading
reading --微信读书进度 100% 或用户明确确认读完--> completed
```

- 尚未开读时，读前完成后给出结果并询问用户是否决定开始阅读；未确认时停止。
- 若精确进度显示已经开读或读完，保留实际状态，把结果标为“回溯式读前分析”，不要再询问是否开始；分别提示可进入读中建档/同步，或已具备读后复盘条件。
- 用户确认开始但没有提供 Obsidian 目录时，只询问目录，不创建文件。
- 达到 100% 时只说明已具备读后复盘条件；除非用户同时要求复盘，否则等待确认。
- 微信读书没有目标书或无法取得进度时，允许用户手动提供进度，并把来源标为 `manual`。

## 保持同一本书

跨阶段优先复用 `douban_subject_id`、`weread_book_id`、ISBN、作者和版本。若新数据指向另一个版本：

1. 说明差异是否影响正文、章节或评分；
2. 不影响内容时保留当前阅读版本，同时把评分版本标清；
3. 会影响阅读策略或笔记定位时，请用户确认后再继续。

## 共同边界

- 不泄露微信读书 API Key、Cookie、私密书架或与当前任务无关的私人笔记。
- 不把评分高低直接等同于作品质量，也不把两个平台的评分人数混为一谈。
- 不编造目录、写作年份、作者意图、划线、用户观点或已达成的一致。
- 不用摘要代替阅读；所有推断都必须与事实、原笔记和用户原话分开。
- 更新已有书籍文件时，只改受管区块和明确的受管 frontmatter 字段。
