---
name: continue-reading
description: Maintain the active-reading stage for a confirmed book by creating or safely updating one Obsidian Markdown note, syncing exact WeRead progress with manual fallback, and appending discussion snapshots that preserve the user's confusion and genuinely agreed viewpoint. Use after the user confirms they are reading, or when they ask to record progress or discuss the book.
---

# Continue Reading

在用户已经决定阅读后建立并维护一本书的单文件记录。此 Skill 负责建档、进度和讨论，不提前执行读后总结。

## 必须先过的门槛

读取 [生命周期协议](../../references/lifecycle-contract.md)、[质量门禁](../../references/quality-gates.md) 和 [书籍笔记模板](../../templates/book-reading.md)。开始写文件前必须同时确认：

1. 用户明确表示将开始或正在阅读这本书；
2. 用户指定了 Obsidian vault 内的目标文件夹。

缺少第一项时，请用户确认是否开始阅读；缺少第二项时，只询问目标文件夹。不得自行猜测 vault，不得在默认 `books/` 路径先建文件。

若没有读前研究结果，先读取并执行 [Prepare Reading](../prepare-reading/SKILL.md)，再把结果用于建档；用户已明确确认阅读时无需重复询问。

## 1. 创建或接管书籍文件

默认文件名为 `<书名>.md`。仅移除路径分隔符、控制字符和当前系统不允许的字符，保留中文书名。写入前先检查目标：

- 文件不存在：从模板创建，状态设为 `reading`，填入读前信息；
- 文件已存在且是同一本书：保留用户自由笔记，只初始化缺失区块或更新受管区块；
- 文件已存在但身份不一致：停止并请用户选择新文件名；
- 不得静默覆盖整份文件。

在 frontmatter 中至少维护书名、作者、状态、豆瓣条目、微信读书 `bookId`、创建/开始/同步时间、进度和进度来源。只修改生命周期协议列出的受管字段。

## 2. 同步阅读进度

定位并读取已安装 `weread-skills` 的 `SKILL.md`，再从同一目录读取阅读数据与书籍能力说明（通常为 `readdata.md`、`book.md`；若安装包使用 `references/`，则读取其中同名文件），使用当前已确认的 `bookId` 获取精确进度。

记录一行：

```text
日期时间 | 进度 | 当前章节/位置 | 累计时长 | 来源 | 备注
```

规则：

- 使用阅读数据中的 `progress`（0–100），不要从书架最近更新时间、笔记数或 `finishReading` 猜进度；
- 用章节目录把 `chapterUid` 映射为真实章节名；映射失败时保留位置 ID 并标“章节名未取得”；
- 累计时长可能为 0 或缺失，只如实记录；
- 同一时间点与同一进度不重复追加；
- 微信读书中无此书、接口不可用或用户线下阅读时，请用户提供手动进度，来源写 `manual`；
- 手动数据不得伪装成微信读书同步结果。

同步后更新 frontmatter 的 `progress_percent`、`progress_source` 和 `last_synced_at`。只有精确进度为 100%，或用户明确确认读完，才提示可以进入读后阶段。

## 3. 讨论与快照

仅在用户提出困惑、想比较观点或要求讨论时触发。讨论时：

1. 先复述用户的具体困惑并确认讨论对象；
2. 区分书中主张、外部证据、用户判断和系统解释；
3. 提出有助于澄清的反例、边界或替代解释；
4. 收束时确认双方是否真的形成共同观点。

把结果追加到“讨论快照”表，关键列必须是：

```text
时间 | 我的困惑 | 达成一致的观点
```

可增加“未决问题/证据”列，但不能缺少前三列。若用户未表示同意，填写“未达成一致”，并记录仍有分歧的点；不要替用户制造共识。用户的困惑可忠实压缩，必要时保留一句短原话。

## 4. 安全更新

- 更新前读取完整文件，识别所有受管标记。
- 只替换对应受管区块或在表格末尾追加行。
- 保留“我的自由笔记”和受管标记之外的全部内容与顺序。
- 写后重新读取文件，确认 frontmatter 可解析、标记成对、表格列数一致且链接未损坏。
- 返回实际文件路径、写入了哪些区块，以及本次进度来源。
- 交付前执行质量门禁的 D0–D3；任何关键失败都停止写入并说明原因。
