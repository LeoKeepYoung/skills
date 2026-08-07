# 书籍识别与阅读路由

在检索双平台数据和分析作品前执行本参考。目标是确认用户指向的作品与版本，并决定分析重心。

## 规范化请求

保留用户原始输入，并整理：

```yaml
title: string
author: string | null
original_title: string | null
isbn: string | null
edition: string | null
language: string
user_goal: string | null
provided_text: string | null
```

缺失字段保持 `null`，不要为了完整而猜测。

## 确认身份

1. 核验标准书名、作者、原文名和首次出版信息。
2. 判断输入是整本书、文集、选集、系列、章节还是文章。
3. 比较同名作品、不同译名、修订版、合集和中文版本的实质差异。
4. 对会改变正文或分析结论的身份事实进行交叉核验，优先使用作者、出版社、图书馆或权威书目来源。
5. 将豆瓣与微信读书条目分别绑定到具体版本；不能确认是同一内容时保留两套版本说明。
6. 给出身份置信度。低于 `0.8` 时列出候选和区分点，等待用户确认。

记录：

```yaml
identity:
  title: string
  original_title: string | null
  author: string
  first_publication_year: integer | null
  work_form: novel | essays | memoir | philosophy | method | textbook | other
  edition_note: string | null
  identification_confidence: number
  analysis_scope: metadata_only | pre_reading | text_grounded
```

只有目录或简介时，最高使用 `pre_reading`；只有正文、可定位章节或用户提供的具体文本才能使用 `text_grounded`。

## 选择阅读模式

判断作品主要给读者提供什么，而不只贴体裁标签：

- `experience`：经验、情绪、人物世界或生命感受；
- `argument`：概念、判断和论证；
- `method`：完成任务或改善能力的方法；
- `knowledge`：专业领域的知识结构。

选择一个主模式；只有次模式会显著改变阅读方式时才保留一个不同的次模式。用一句话说明读者承诺，并按作品实际情况分配 Context、Author、Work 分析权重。

可用以下基线起步，不得机械复制：

```yaml
experience: {context: 35, author: 30, work: 35}
argument: {context: 20, author: 15, work: 65}
method: {context: 10, author: 10, work: 80}
knowledge: {context: 15, author: 5, work: 80}
```

三项权重总和必须为 100 且均大于 0。路由置信度低于 `0.75` 时说明缺少什么资料，不以确定语气输出。

## 阻断条件

- 同名候选无法排除；
- 版本差异会改变正文或目录；
- 输入不是一本书但被误识别为书；
- 作者、书名或平台条目互相冲突。

阻断时只输出候选、区分依据和一个最小确认问题，不继续作者动机、创作背景或章节策略分析。
