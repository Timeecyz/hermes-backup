---
name: dreamina
description: 即梦AI（Dreamina）图片/视频生成 CLI 工具。当用户需要生成研学营/公众号配图、或用即梦AI生成任何图片/视频时使用。安装后通过 `dreamina login --headless` + QR扫码完成认证，支持文生图、视频生成、图生视频等任务。
---

# Dreamina（即梦AI）CLI

即梦是字节跳动旗下 AI 图像/视频生成平台，CLI 版本支持本地自动化调用。

## 安装

```bash
curl -s https://jimeng.jianying.com/cli | bash
```

安装位置：
- 二进制：`~/.local/bin/dreamina`
- Skill文档：`~/.dreamina_cli/dreamina/SKILL.md`

## 登录认证（QR扫码流程）

```bash
dreamina login --headless
```

`--headless` 会输出 `verification_uri` + `user_code` + `device_code`，然后退出不轮询。

**必须通过 `message` 工具发送二维码图片给用户，不能只发文字或路径。**

### 生成二维码的方法

即梦 QR 登录地址较长，需要用 qrcode 库生成图片：

```python
# 用 Hermes venv 的 Python，不要用系统 Python
/home/agentuser/.hermes/hermes-agent/venv/bin/python3 -c "
import qrcode
url = 'https://jimeng.jianying.com/ai-tool/cli-auth?verification_uri=...'
qr = qrcode.make(url)
qr.save('/tmp/dreamina_qr.png')
print('done')
"
```

保存路径建议 `/tmp/dreamina_qr.png`，然后用 `message` 工具发送：

```
send_message(action='send', media='/tmp/dreamina_qr.png', message='请用抖音App扫描此二维码并在手机上确认授权。', target='feishu:ou_xxx')
```

> ⚠️ 注意：系统 Python（`/usr/bin/python3`）通常有 `externally-managed-environment` 限制，无法直接 `pip install qrcode`。要用 Hermes venv 的 Python。

### 登录成功判断

登录完成后，下一次 `dreamina login --headless` 会输出 `[DREAMINA:LOGIN_SUCCESS]` 或 `[DREAMINA:LOGIN_REUSED]`，此时必须告知用户登录成功。

## 常用命令

```bash
dreamina -h                      # 全局帮助
dreamina login -h                # 登录子命令帮助
dreamina user_credit             # 查询账户积分
dreamina list_task               # 查看历史任务
dreamina query_result --submit_id=<id>  # 查询任务结果
```

具体图片/视频生成子命令，先查帮助：
```bash
dreamina <子命令> -h
```

## 关键规则

- **文字渲染**：即梦对中文草书/艺术字支持差（乱码），研学营配图如需精准中文文字，建议用 Nano Banana Pro（Gemini 3 Pro Image）或豆包生成图片，我负责排版叠加文字。
- **异步任务**：生成任务是异步的，`submit_id` 存在才能查询结果。`gen_status` 为 `querying` 或 `success` 才算提交成功。
- **积分预检**：运行生成命令前，先 `dreamina user_credit` 确认余额充足。
- **seedance2.0 模型**：质量最高但可能容量受限，不追求极致速度时可不默认使用。

## 蛮子使用场景

蛮子的研学营项目配图有两种方案：
1. **即梦AI** — 适合插画风海报，文字渲染弱，需要我再叠加文字图层
2. **豆包+我排版** — 蛮子用豆包生成，我用 PIL 在图片上叠加精准中文字（推荐）