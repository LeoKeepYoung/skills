---
name: reading
description: Build evidence-aware pre-reading maps that connect a book's historical context, author lens, work structure, and reading strategy. Use when a user names a book and asks for a reading map, reading guide, pre-reading orientation, context-author-work analysis, or an Obsidian-ready reading-map.md; also use when the user explicitly wants facts separated from interpretations and uncertainty.
---

# Reading Coach

为读者建立进入一本书所需的认知坐标。生成阅读入口，不生成章节摘要或作者百科。

## 开始前

将用户信息规范化为：

```yaml
book_request:
  title: string
  author: string | null
  original_title: string | null
  isbn: string | null
  language: string
  edition: string | null
  user_goal: string | null
  reading_progress: string | null
  provided_text: string | null
```

缺省 `language` 为用户当前语言。不要为了填满字段而猜测。

完整运行前必须读取：

- [证据政策](references/evidence-policy.md)
- [质量门禁](references/quality-gates.md)
- [ReadingMapIR Schema](schemas/reading-map.schema.yaml)

需要最终文件时读取 [Markdown 模板](templates/reading-map.md)。

## 工作流

严格按以下顺序推进。前一阶段被阻断时，不继续生成貌似完整的结果。

1. **识别书籍。** 读取并执行 [Book Resolver](skills/book-resolver/SKILL.md)。消除同名书、译名、作者、合集与版本歧义，确定 `analysis_scope`。
2. **选择路由。** 读取并执行 [Book Router](skills/book-router/SKILL.md)。选择主次阅读模式，给 Context、Author、Work 分配总和为 100 的权重。
3. **建立三层地图。** 分别读取并执行 [Context Analysis](skills/context-analysis/SKILL.md)、[Author Lens](skills/author-lens/SKILL.md) 与 [Work Map](skills/work-map/SKILL.md)。按路由权重控制深度，但不得省略任何一层。
4. **生成阅读入口。** 读取并执行 [Reading Entry](skills/reading-entry/SKILL.md)。只整合已有结果，不新增事实。
5. **运行门禁。** 逐项执行 `references/quality-gates.md`，将结果写入 `quality`。把未确认内容写入 `uncertainty`，不得补全。
6. **渲染 Markdown。** 读取并执行 [Markdown Renderer](skills/markdown-renderer/SKILL.md)。Renderer 不得添加分析或事实。
7. **校验结构。** 在可运行脚本的环境中执行：

   ```bash
   python3 scripts/validate_reading_map.py path/to/reading-map-ir.yaml --strict
   ```

   若当前 Python 没有 PyYAML 且可使用 `uv`，改为：

   ```bash
   uv run --with pyyaml python scripts/validate_reading_map.py path/to/reading-map-ir.yaml --strict
   ```

   修复所有错误后再交付。若只能在对话中输出，按相同规则人工校验。

## 分析深度

只允许以下三级：

- `metadata_only`：只确认身份、版本与可用资料。
- `pre_reading`：依据可靠外部资料生成阅读前地图。
- `text_grounded`：已获得目录、正文或用户提供的具体文本，可分析文本结构和语言。

只收到书名时，最高使用 `pre_reading`。不要声称读过未提供或未获取的全文。目录只能支持结构判断，不能支持对具体语言、意象或细节的断言。

## 研究与证据

优先使用作者或出版社资料、图书馆目录、学术来源和高质量评论。对会影响书籍识别或核心解释的事实进行交叉核验。不要把搜索摘要当作来源。

将每个关键主张标记为：

- `fact`
- `accepted_interpretation`
- `system_inference`
- `open_question`

在正文中使用自然语言区分事实与解释；在 `evidence` 中保留可追踪来源。无法核实的内容进入 `uncertainty`。

## 输出要求

先构建完整 `ReadingMapIR`，再渲染文章。最终结果至少包含：

- 一个明确阅读重点；
- 一个容易误读点及纠正；
- 一个阅读中的观察问题；
- 一个迁移边界；
- 证据与不确定性说明。

用户要求保存文件时，默认写入：

```text
books/<author>/<book-slug>/reading-map.md
```

对非拉丁书名生成简短、稳定的 ASCII slug；存在同名冲突时追加出版年份。不得覆盖已有文件，除非用户明确要求更新。

## 失败处理

- 身份置信度低于 `0.8`：输出候选项和需要确认的问题，停止后续分析。
- 作者资料不足：允许继续，但压缩作者层，并声明不推断作者动机。
- 缺少正文或目录：降级到 `pre_reading`。
- 来源冲突：并列呈现不同说法，说明冲突影响。
- 作品模式混合：保留主模式和次模式，不强制单一分类。

## 边界

不要代替用户阅读整本书，不生成完整章节摘要，不编造金句、目录、ISBN、译者或出版信息，不远距离诊断作者人格，不把叙述者等同于作者，不强行把每本书变成行动清单。
