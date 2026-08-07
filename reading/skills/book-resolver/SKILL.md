---
name: book-resolver
description: Resolve a book's canonical identity, author, original title, publication, work form, edition differences, and permitted analysis scope. Use when a title, translation, edition, collection, chapter, or author may be ambiguous, or before any Reading Coach analysis begins.
---

# Book Resolver

准确识别用户所指的作品。身份未过门禁时停止，不要让后续分析建立在猜测上。

## 输入

接收完整 `book_request`。保留用户原始书名与版本线索。

## 流程

1. 搜索标准书名、作者、原文名和首次出版信息。
2. 判断输入是整本书、文集、演讲集、选集、系列名、章节名还是文章名。
3. 比较同名作品、不同译名、修订版与中文版本的实质差异。
4. 至少交叉核验会改变身份判断的关键事实。优先使用出版社、作者、图书馆或权威书目来源。
5. 按可用材料确定 `analysis_scope`。只有目录或简介时不得标记为 `text_grounded`。
6. 给出置信度。低于 `0.8` 时返回候选项并停止。

## 输出契约

```yaml
identity:
  title_zh: string
  title_original: string | null
  author: string
  first_publication_year: integer | null
  work_form: novel | essays | memoir | philosophy | method | textbook | other
  edition_note: string | null
  identification_confidence: number
  analysis_scope: metadata_only | pre_reading | text_grounded
```

被阻断时输出：

```yaml
status: blocked
reason: ambiguous_book_identity
candidates:
  - title: string
    author: string
    distinguishing_detail: string
question_for_user: string
```

## 门禁

确认书名、作者、原文名、版本与作品形式互相一致。版本差异可能改变正文时，必须明确具体版本。

## 禁止

不要随意选择同名书，不要编造 ISBN、译者或年份，不要混合不同版本，不要把章节名当作书名。来源未确认时使用 `null`，不要补全。
