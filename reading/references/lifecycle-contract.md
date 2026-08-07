# Reading 生命周期协议

本文件定义三个阶段共享的状态、书籍身份、微信读书数据语义和 Obsidian 写入边界。

## 目录

1. 状态机
2. 书籍身份
3. 微信读书调用约束
4. 单文件约定
5. 证据与时间
6. 隐私与最小读取

## 1. 状态机

| 状态 | 含义 | 进入条件 | 允许动作 |
|---|---|---|---|
| `planned` | 已完成或正在进行读前研究，尚未确认阅读 | 默认 | 研究、比较、制定策略 |
| `reading` | 用户明确开始/正在阅读 | 用户确认 + Obsidian 目录已确认 | 建档、同步进度、讨论 |
| `completed` | 书已读完 | 微信读书精确进度 100，或用户明确手动确认 | 回扫、总结、三问、输出选题、可选推荐 |

不得根据模型猜测跳过门槛。状态变化要记录时间和来源。

## 2. 书籍身份

跨阶段保存并优先复用：

```yaml
title: string
original_title: string | null
author: string
isbn: string | null
edition: string | null
douban_subject_id: string | null
douban_url: string | null
weread_book_id: string | null
weread_url: string | null
```

书名和作者只用于初筛；ISBN、平台 ID 和版本信息用于稳定匹配。译本、修订版或合集会改变正文/章节时必须由用户确认。

## 3. 微信读书调用约束

微信读书能力由已安装的 `weread-skills` 提供。调用前先定位其主 `SKILL.md`，再从同一目录读取本阶段需要的能力说明，并服从其中的最新版本、网关、分页和升级指令。能力说明可能直接位于 Skill 根目录（如 `search.md`），也可能位于 `references/`；以已安装包的真实目录为准，不写死其中一种布局。

- 凭据只从已配置环境读取，不写入仓库、笔记、日志或答复。
- 搜索评分字段为 `newRating`（0–100），评分人数为 `newRatingCount`。
- `readingCount` 是阅读人数，不是评分人数。
- 精确进度来自阅读数据的 `progress`（0–100）；书架更新时间不是进度。
- 全量个人笔记由“划线”和分页的“我的想法/书评”共同组成。
- 每次同步记录时间；平台数据缺失时写明降级路径。
- 若响应包含升级提示，停止当前调用并先按官方 Skill 指引升级。

## 4. 单文件约定

读前内容、进度、讨论与读后复盘共用 `<用户确认的 Obsidian 目录>/<书名>.md`。新文件使用 [book-reading.md](../templates/book-reading.md)。

### 受管 frontmatter

仅自动维护：

```yaml
type: reading-note
title: string
original_title: string | null
author: string
isbn: string | null
edition: string | null
status: planned | reading | completed
douban_subject_id: string | null
douban_url: string | null
weread_book_id: string | null
weread_url: string | null
cover: string | null
created_at: ISO-8601 datetime
reading_started_at: ISO-8601 datetime | null
completed_at: ISO-8601 datetime | null
last_synced_at: ISO-8601 datetime | null
progress_percent: integer | null
progress_source: weread | manual | null
completion_source: weread | manual | null
```

未知值用 `null` 或空字符串，不能猜测。

### 受管区块

模板用成对 HTML 注释标记四个区块：

```text
reading:pre
reading:progress
reading:discussion
reading:post
```

更新规则：

1. 写前读取完整文件并确认开始/结束标记各一个且顺序正确；
2. 只替换目标区块内部内容；
3. 进度和讨论优先追加行，避免重建整张表；
4. 所有标记外内容均视为用户内容；
5. 标记损坏时停止并说明，不猜测截断范围；
6. 写后重新读取并检查 frontmatter、标记和表格。

## 5. 证据与时间

- 平台评分会变化，必须绑定具体条目/版本和访问时间。
- 作者的“写作区间”“完成时间”“出版时间”是不同字段；只有证据支持时才能合并。
- 作者意图优先来自作者直接陈述；没有直接来源时标记为解释。
- 微信读书划线不等于用户赞同；系统从笔记推测观点时必须列出依据。
- 时间使用用户所在时区，统一写 ISO 8601 或 `YYYY-MM-DD HH:mm`，同一文件保持一致。

## 6. 隐私与最小读取

书架和笔记只用于当前阅读任务。先读取概览，再深入少量相关条目；不得展示与结论无关的私密书单或笔记。落档前省略账号标识、接口凭据和不必要的内部 ID。
