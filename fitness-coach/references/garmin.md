# Garmin 接入与数据解释

用户已希望将自己的 Garmin 数据用于减脂增肌建议；在此范围内读取相关时间窗口即可，不必每次重复询问读取许可。若尚未登录，先准备运行环境，再让用户在自己的终端完成登录，不让用户在聊天中发送密码或验证码。

## 选择数据来源

优先使用已连接且能读取所需指标的 Garmin 工具。没有直连时使用随技能提供的 [garmin_sync.py](../scripts/garmin_sync.py)。它使用非官方开源客户端 `garminconnect`，通过 Garmin 的登录服务访问账号，仅调用数据读取接口，不上传、修改或删除活动与训练计划。账号令牌本身不保证只读，需像密码一样保管。

Garmin 官方 Connect Developer Program 面向企业接入并需要申请；不能把安装本技能说成获得了官方 API 授权。也不要把可向 Garmin 发送课表的第三方工具等同于能读取全部睡眠与健康指标的连接。[Garmin 官方 FAQ](https://developer.garmin.com/gc-developer-program/program-faq/)

## 首次安装与登录

脚本需要 Python 3.12 或更新版本。固定客户端版本见 [requirements-garmin.txt](../scripts/requirements-garmin.txt)。已有独立运行环境时复用；否则在技能目录下执行以下命令，用 `uv` 创建仓库外的环境：

```bash
uv venv --python 3.12 "$HOME/.local/share/fitness-coach/venv"
uv pip install --python "$HOME/.local/share/fitness-coach/venv/bin/python" -r scripts/requirements-garmin.txt
```

没有 `uv` 但已安装 Python 3.12 时，可用 `python3.12 -m venv` 创建同一目录，再用该环境的 `python -m pip install -r scripts/requirements-garmin.txt` 安装依赖。不要把环境或令牌放到公开仓库。

用户已确认使用中国区 `cn`（`connect.garmin.cn`），脚本默认使用此区域，不重复询问。下面的命令仍显式写出 `--region cn` 便于检查。以后用户换到国际区 `global`（`connect.garmin.com`）时再更改参数，不能根据所在地猜测账号区域。

用户在自己的交互终端执行：

```bash
"$HOME/.local/share/fitness-coach/venv/bin/python" scripts/garmin_sync.py login --region cn
```

登录时输入邮箱、隐藏输入的密码，以及需要时的验证码。凭据通过客户端传给 Garmin，令牌存到本机私有目录；不要由助手读入、回显、复制或提交令牌。已有令牌但过期时仍通过这个命令重新登录。[客户端认证与存储说明](https://github.com/cyberjunky/python-garminconnect#-authentication)

## 检查与读取

```bash
# 只检查本地缓存是否存在，不证明远端登录仍然有效。
"$HOME/.local/share/fitness-coach/venv/bin/python" scripts/garmin_sync.py status --region cn

# 最近七个完整自然日；运行前让手表与 Garmin Connect 完成同步。
"$HOME/.local/share/fitness-coach/venv/bin/python" scripts/garmin_sync.py sync --region cn --days 7 --timezone Asia/Shanghai

# 自定义结束日及窗口；最多三十一天，结束日包含在内。
"$HOME/.local/share/fitness-coach/venv/bin/python" scripts/garmin_sync.py sync --region cn --days 14 --end 2026-10-13 --timezone Asia/Shanghai
```

默认时区为 Asia/Shanghai，可按用户实际 Garmin 日历时区修改。时区只决定默认结束日期；活动使用 Garmin 的本地开始时间，日汇总使用 Garmin 日历日期，不擅自把它们当作 UTC 再平移。旅行或跨时区时说明日期可能不完全可比。

默认目录为 `~/.local/share/fitness-coach/garmin/<region>/`：`tokens/` 保存登录会话，`snapshots/` 保存每次读取的摘要，`latest.json` 指向最近一次含有观测值的摘要内容。摘要和令牌文件仅当前用户可读写；脚本拒绝把状态目录放进 Git 仓库。可用 `--state-dir` 指定其他私人目录，后续使用相同路径。

终端只返回状态、摘要路径与活动数量，按返回的具体路径读取本次结果。不要在失败后把旧 `latest.json` 当成本次新数据；旧文件的 `fetched_at_utc` 和日期范围必须展示清楚。

## 指标与覆盖范围

| 数据 | 用法与限制 |
|---|---|
| 活动类型、时长、距离、心率 | 判断训练安排与实际负荷；按活动 ID 去重，不读取 GPS 轨迹、地址或自由文本标题 |
| 步数、强度分钟 | 观察日常活动变化；零与无数据分开 |
| 睡眠时长、睡眠分数 | 结合本人精神和疲劳状态观察趋势，不能诊断睡眠疾病 |
| HRV、静息心率、压力、Body Battery | 与个人基线及连续几天表现对比；不设所有人通用的好坏阈值 |
| 体重、体脂估计（账号有记录时） | 结合腰围和力量观察趋势；体脂秤估计不等于精确的肌肉或脂肪变化 |
| 日总消耗、活动消耗估计 | 仅作参考；日总消耗与运动热量不能重复相加，不用来逐卡补吃 |

并非所有设备或账号都提供全部指标。摘要按 `stats`、`sleep`、`hrv`、`body_composition`、`activities` 标出 `ok`、`no_data` 或 `error`，缺失值为 `null`；睡眠使用小时、HRV 使用毫秒、心率使用 bpm、体重从源数据克换算为 kg。保留日期、来源、范围和实际读取时间，避免把本日未完成数据与完整日直接比较。

体重记录没有返回测量日期时保持日期缺失，不能用拉取日期替代测量日期，也不将这类记录用于计算逐日变化。

活动最多读取五页、每页一百条；达到上限或返回异常时标记不完整，不把已读取的部分当成全量。退出码为：`0` 正常完成，`2` 登录／配置／请求中止，`3` 部分指标失败，`4` 没有可用观测值。`0` 也不代表每种指标每天都有数据，需检查各项状态。

遇到 `authentication_required` 或 `rate_limited` 立即停止，不自动反复登录；提示重新登录或稍后手动重试。部分指标不可用时保留其状态和其他成功数据；全空结果不覆盖上一份可用摘要。客户端版本更新或接口变化时先验证返回结构与单位，再更新依赖，不能静默填补缺失数据。

## 验证与边界

无需账号即可运行 [本地测试](../scripts/test_garmin_sync.py)：

```bash
"$HOME/.local/share/fitness-coach/venv/bin/python" -m unittest discover -s scripts -p 'test_garmin_sync.py' -v
```

测试覆盖缺失值与单位、分页去重、权限／限流中止和私有文件存储，不能代替用户账号实测。首次真实读取前明确说“接入已准备，账号尚待登录”；只有返回真实数据后才报告成功与实际覆盖范围。

默认不创建定时同步，不调用写入接口，不读取与训练建议无关的健康数据。若用户不使用第三方登录，可继续处理其主动提供的 Garmin 导出文件；先核对格式与日期范围，不要求重新分享账号凭据。
