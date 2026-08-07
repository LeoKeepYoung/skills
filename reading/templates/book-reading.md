---
type: reading-note
title: "{{ title }}"
original_title: "{{ original_title }}"
author: "{{ author }}"
isbn: "{{ isbn }}"
edition: "{{ edition }}"
status: reading
douban_subject_id: "{{ douban_subject_id }}"
douban_url: "{{ douban_url }}"
weread_book_id: "{{ weread_book_id }}"
weread_url: "{{ weread_url }}"
cover: "{{ cover }}"
created_at: "{{ created_at }}"
reading_started_at: "{{ reading_started_at }}"
completed_at: null
last_synced_at: "{{ last_synced_at }}"
progress_percent: {{ progress_percent }}
progress_source: "{{ progress_source }}"
completion_source: null
---

# 《{{ title }}》

{{ cover_markdown }}

<!-- reading:pre:start -->
## 读前｜进入这本书

### 基本信息与双平台评分

| 平台 | 书籍版本与链接 | 评分 | 评分人数 | 访问时间 |
|---|---|---:|---:|---|
| 豆瓣读书 | {{ douban_entry }} | {{ douban_rating }} | {{ douban_rating_count }} | {{ douban_accessed_at }} |
| 微信读书 | {{ weread_entry }} | {{ weread_rating }} | {{ weread_rating_count }} | {{ weread_accessed_at }} |

> [!note] 版本说明
> {{ edition_note }}

### 作者与作品时间轴

| 年份/区间 | 身份、事件或作品 | 与本书的关系 | 证据状态 |
|---|---|---|---|
| {{ period }} | {{ event }} | {{ relation }} | {{ evidence_status }} |

> [!important] 本书的创作区间
> {{ creation_interval }}

### 创作背景与表达意图

{{ creation_context }}

### 与我的既有阅读连接

{{ personal_connections }}

### 阅读路线

| 阅读范围 | 阅读重点 | 阅读提醒 |
|---|---|---|
| {{ reading_range_1 }} | {{ reading_focus_1 }} | {{ reading_reminder_1 }} |
| {{ reading_range_2 }} | {{ reading_focus_2 }} | {{ reading_reminder_2 }} |
| {{ reading_range_3 }} | {{ reading_focus_3 }} | {{ reading_reminder_3 }} |

> “阅读提醒”同时承载容易误读之处、适用条件和迁移边界；不再另设独立章节。

#### 阅读中的问题

1. {{ question_1 }}
2. {{ question_2 }}
3. {{ question_3 }}

### 读前来源与不确定性

{{ pre_sources_and_uncertainty }}
<!-- reading:pre:end -->

<!-- reading:progress:start -->
## 读中｜阅读进度

| 日期时间 | 进度 | 当前章节/位置 | 累计时长 | 来源 | 备注 |
|---|---:|---|---:|---|---|
| {{ progress_time }} | {{ progress_percent }}% | {{ current_location }} | {{ cumulative_time }} | {{ progress_source }} | {{ progress_note }} |
<!-- reading:progress:end -->

<!-- reading:discussion:start -->
## 读中｜讨论快照

| 时间 | 我的困惑 | 达成一致的观点 | 未决问题/证据 |
|---|---|---|---|
|  |  |  |  |
<!-- reading:discussion:end -->

## 我的自由笔记

> 此处及其他受管标记之外的内容由我自由维护，Skill 不会覆盖。

<!-- reading:post:start -->
## 读后｜回看与延伸

### 笔记回扫

**直接记录：** {{ direct_notes }}

**模式归纳：** {{ pattern_summary }}

**谨慎推测：** {{ cautious_inference }}

### 我的所学所得

{{ experience_summary }}

### 读后三问

1. **{{ reflection_question_1 }}**
   - 回答：{{ reflection_answer_1 }}
2. **{{ reflection_question_2 }}**
   - 回答：{{ reflection_answer_2 }}
3. **{{ reflection_question_3 }}**
   - 回答：{{ reflection_answer_3 }}

### 输出选题

| 选题 | 核心问题/表达方向 | 推荐依据 | 建议形式 | 决定 |
|---|---|---|---|---|
| {{ output_topic_1 }} | {{ output_topic_1_question }} | {{ output_topic_1_basis }} | {{ output_topic_1_format }} | {{ output_topic_1_decision }} |
| {{ output_topic_2 }} | {{ output_topic_2_question }} | {{ output_topic_2_basis }} | {{ output_topic_2_format }} | {{ output_topic_2_decision }} |
| {{ output_topic_3 }} | {{ output_topic_3_question }} | {{ output_topic_3_basis }} | {{ output_topic_3_format }} | {{ output_topic_3_decision }} |

> 未使用的候选行应删除；用户明确决定前统一标记为“待决定”。

### 后续阅读（可选）

{{ recommendations }}

### 数据完整性与不确定性

{{ post_sources_and_uncertainty }}
<!-- reading:post:end -->
