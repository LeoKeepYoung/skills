# Reading Coach Skill Design Spec v1.0

**状态：** MVP implementation
**核心产物：** `reading-map.md`
**运行宿主：** Codex / ChatGPT
**技术路线：** 顶层 `reading` 负责调度，七个职责 Skill 提供稳定、可复用的阅读分析能力。

## 1. 项目目标

Reading Coach 不是书籍摘要工具。

它的目标是：

> 用户输入一本书的名称后，系统从时代、作者、作品三个层面，为读者建立进入这本书所需的认知坐标。

系统帮助读者回答：

1. 这本书诞生于怎样的世界？
2. 为什么是这个作者写出了它？
3. 这本书在表达、解释或解决什么？
4. 应该以什么方式进入这本书？
5. 哪些内容是事实，哪些只是解释？

## 2. 非目标

v1 不负责：

- 代替用户阅读整本书；
- 生成完整章节摘要；
- 自动提炼所有金句；
- 建立个人读书笔记；
- 强行把每本书转化为行动建议；
- 对作者进行未经证据支持的心理诊断；
- 根据书名假装已经读过全文；
- 支持复杂个人知识图谱。

## 3. 核心设计原则

### 3.1 Markdown First

```text
书籍输入
   ↓
结构化分析结果
   ↓
ReadingMapIR
   ↓
Markdown Renderer
   ↓
reading-map.md
```

HTML、PDF、Obsidian 页面属于展示层，不影响核心分析结构。

### 3.2 三层始终存在，权重动态调整

所有书保留：

- Context：时代与环境；
- Author：作者经历与观察视角；
- Work：作品本身。

建议初始权重：

```yaml
experience:
  context: 35
  author: 30
  work: 35
argument:
  context: 20
  author: 15
  work: 65
method:
  context: 10
  author: 10
  work: 80
knowledge:
  context: 15
  author: 5
  work: 80
```

权重控制分析深度，不表示任何层可以完全省略。

### 3.3 事实与解释分离

```yaml
claim_type:
  fact: 可核验事实
  accepted_interpretation: 较普遍的学术或评论界解释
  system_inference: 系统根据事实作出的推断
  open_question: 暂时无法确认的问题
```

禁止把推断写成事实。详细规则见 `references/evidence-policy.md`。

### 3.4 不知道全文，不得假装分析全文

```yaml
analysis_scope:
  metadata_only: 只确认身份和版本
  pre_reading: 根据可靠资料生成阅读前地图
  text_grounded: 已获得目录、正文或用户提供的具体文本
```

只输入书名时，默认最高生成 `pre_reading` 结果。

### 3.5 阅读入口优先于百科知识

每条背景信息都必须回答：

> 这件事为什么有助于读者理解这本书？

与作品没有关系的传记或历史资料应删除。

## 4. 系统架构

```text
用户输入书名
      ↓
Book Resolver
      ↓
Book Router
      ↓
┌─────────────┬─────────────┬─────────────┐
│ Context     │ Author Lens │ Work Map    │
│ Analysis    │             │             │
└─────────────┴─────────────┴─────────────┘
      ↓
Reading Entry
      ↓
Quality Gates
      ↓
Markdown Renderer
      ↓
reading-map.md
```

Quality Gates 作为横向规则存在，不单独生产内容。

## 5. 统一输入契约

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

最小输入：

```yaml
book_request:
  title: 每一句话语都坐着别的眼睛
  language: zh-CN
```

## 6. 统一中间结构

`ReadingMapIR` 文档根节点就是以下 mapping，不再额外嵌套 `reading_map`：

```yaml
identity: {}
routing: {}
context: {}
author: {}
work: {}
entry: {}
evidence: []
uncertainty: []
quality: {}
```

完整机器可读定义见 `schemas/reading-map.schema.yaml`。

## 7. Skill 职责

### 7.1 Book Resolver

准确识别标准书名、作者、原文名、首次出版时间、作品形式和版本差异，并确定分析范围。

身份置信度低于 `0.8` 时停止，输出候选项和确认问题。

### 7.2 Book Router

判断作品主要向读者提供什么：

- `experience`：经验、情绪、人物世界或生命感受；
- `argument`：概念、判断和论证；
- `method`：完成任务或改善能力的方法；
- `knowledge`：专业领域的知识结构。

输出主模式、可选次模式、读者承诺、三层权重、路由理由和置信度。三项权重总和必须为 100。

### 7.3 Context Analysis

回答：

> 这本书面对的是怎样的世界，那个世界为什么需要这本书？

至少建立一条：

```text
环境事实 → 人的处境 → 作者面对的问题 → 作品出现的必要性
```

### 7.4 Author Lens

回答：

> 为什么是这个人，以这种方式写出了这本书？

只保留与本书有关的经历、长期问题、观察方式和表达风格。不要输出完整传记。

### 7.5 Work Map

回答：

> 这本书本身到底提供了什么？

按阅读模式动态分析核心任务、读者承诺、结构、概念、阅读重点、容易误读处和边界。不得退化为摘要器。

### 7.6 Reading Entry

整合三层结果：

```text
什么样的世界
   ↓
塑造了什么样的作者视角
   ↓
产生了什么样的作品
```

输出具体阅读姿势、观察问题和迁移边界，不新增事实。

### 7.7 Markdown Renderer

将 `ReadingMapIR` 转换为稳定、可读、适合 Obsidian 的 Markdown。Renderer 不得增加新的分析和事实。

默认文件位置：

```text
books/<author>/<book-slug>/reading-map.md
```

## 8. Quality Gates

完整执行标准见 `references/quality-gates.md`。

### Gate 0：身份

检查书名、作者、原文名、版本、作品形式。

### Gate 1：路由

检查模式理由、权重、主次模式及 `routing.confidence >= 0.75`。

### Gate 2：证据

检查关键事实、解释标签、来源冲突和不确定性。

### Gate 3：因果链

检查：

```text
Context → Author
Author → Work
Context → Work
```

每条连接必须说明中间机制。

### Gate 4：过度解释

检查单一原因、心理诊断、唯一意象解释和时代万能论。

### Gate 5：摘要漂移

结果不能只剩普通书籍简介或长篇内容摘要。

### Gate 6：阅读价值

至少提供一个明确阅读重点、一个误读及纠正、一个观察问题和一个迁移边界。

### Gate 7：完整性

必须存在 `identity`、`routing`、`context`、`author`、`work`、`entry`、`evidence`、`uncertainty` 与 `quality`。

## 9. 失败处理

### 9.1 书籍无法确认

```yaml
status: blocked
reason: ambiguous_book_identity
candidates:
  - title: string
    author: string
question_for_user: string
```

不继续分析。

### 9.2 作者资料不足

允许生成作品地图，但声明：

> 作者层资料不足，本次仅提供有限背景，不对作者动机作推断。

### 9.3 无法获得正文或目录

将范围降级为 `pre_reading`，不得输出详细章节、具体意象或语言判断。

### 9.4 资料冲突

并列呈现不同说法，不自行选择更戏剧化的一种。

### 9.5 作品类型混合

输出主模式和次模式，后续 Skill 按双模式调整。

## 10. 文件结构

```text
reading/
├── DESIGN.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── skills/
│   ├── book-resolver/
│   ├── book-router/
│   ├── context-analysis/
│   ├── author-lens/
│   ├── work-map/
│   ├── reading-entry/
│   └── markdown-renderer/
├── references/
│   ├── evidence-policy.md
│   └── quality-gates.md
├── schemas/
│   └── reading-map.schema.yaml
├── templates/
│   └── reading-map.md
├── scripts/
│   └── validate_reading_map.py
├── evals/
│   ├── cases.yaml
│   └── expected-properties.yaml
└── examples/
    ├── literary-experience.md
    ├── method-book.md
    ├── argument-book.md
    └── knowledge-book.md
```

## 11. MVP 评测

至少覆盖：

- 文学体验：《每一句话语都坐着别的眼睛》；
- 方法工具：《金字塔原理》；
- 思想论证：《幸福之路》；
- 专业知识：《Designing Data-Intensive Applications》。

用例和预期属性见 `evals/`。

## 12. 成功标准

一个合格 Reading Map 应使读者在阅读前能够回答：

1. 我即将进入什么样的世界？
2. 作者为何会关注这个问题？
3. 这本书主要提供什么？
4. 阅读时应该注意什么？
5. 哪些解释只是可能性？
6. 不应该把这本书误用成什么？

系统成功不以长度衡量，而以是否减少读者进入一本书时的语境缺失与阅读误判衡量。
