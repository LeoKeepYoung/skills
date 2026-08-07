---
name: markdown-renderer
description: Render a complete ReadingMapIR into stable, readable, Obsidian-compatible Markdown with YAML frontmatter and evidence and uncertainty sections. Use only after analysis and quality gates are complete; never use it to add facts, interpretations, or missing analysis.
---

# Markdown Renderer

将完整 `ReadingMapIR` 渲染为 `reading-map.md`。只负责表达，不负责分析。

## 输入要求

确认 `identity`、`routing`、`context`、`author`、`work`、`entry`、`evidence`、`uncertainty` 与 `quality` 均存在。质量状态不是 `pass` 时不要伪装成最终版。

## 流程

1. 读取顶层 `templates/reading-map.md` 模板；若独立使用本 Skill，由调用者提供模板。
2. 保持固定章节顺序和 YAML frontmatter 字段。
3. 将结构化列表转换为简洁、自然的 Markdown。合并重复项，不改变原意。
4. 在正文中保留事实、常见解释、系统推断与开放问题的语言边界。
5. 将证据写成可追踪的编号列表或表格；来源链接直接指向支持主张的页面。
6. 将空但允许为空的字段明确写为“资料不足”或“尚待正文验证”，不要删除整个三层章节。
7. 默认输出到 `books/<author>/<book-slug>/reading-map.md`。避免覆盖现有文件。

## 渲染规则

- 使用一个 H1，主章节使用 H2，子章节使用 H3。
- 保持段落短小，优先使用项目列表呈现阅读重点与问题。
- 不输出原始内部置信度，除非它影响读者判断或用户要求查看。
- 不把来源链接集中成无法对应主张的“参考资料堆”。
- 不新增事实，不提高推断强度，不修补上游缺失。

## 失败处理

上游字段缺失时返回缺失字段列表。质量门禁失败时输出“草稿/被阻断”状态和原因，不渲染成可交付最终稿。
