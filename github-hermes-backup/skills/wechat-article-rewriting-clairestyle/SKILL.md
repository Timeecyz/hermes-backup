---
name: wechat-article-rewriting-clairestyle
description: 微信公众号文章全流程重写助手（WARC）。当用户提供微信公众号文章链接、HTML/Markdown文件或明确重写意图时使用此技能。完整流程：抓取文章 → 结构拆解+仿写 → Claire风格重写 → 生成四件套 → 存入本地 → 存入公众号草稿。
强制规则: 1）所有数据必须标注具体出处（机构名+时间+数据值） 2）原文数据必须保留，仅换表达方式，不能删除或模糊化
version: "1.1.1"
icon: 📝
os: linux, macos
tags: wechat, article, rewriting, notion, publish
---

# WARC - 微信公众号Claire风格重写助手

## ⚠️ 配图工具硬规则（2026-06-05）

- **fal.ai / image_generate 已禁用** — 不论什么情况，不再调用
- 所有配图一律由蛮子在豆包/即梦生成，管家只负责上传推送
- 蛮子生成后发给我，我负责：上传素材库 + 推送草稿

---

## 触发条件

满足以下任一条件即自动激活本技能：

1. **微信公众号链接** — 用户发送 mp.weixin.qq.com/s/... 链接
2. **HTML/Markdown文件** — 用户发送 .html 或 .md 文件，或直接粘贴文章正文
3. **播客/非公众号内容** — 用户提供播客文字稿、PDF、Notion笔记等来源，要求改写成公众号文章
4. **明确意图** — 用户说"帮我改成Claire风格"/"改成公众号内容"/"重写"/"写一篇公众号文章"等

用户发送文件后未说明平台时，默认按「不躺平的钱」Claire风格处理。

## 重要规则（必须遵守）

### ⚠️ 数据引用规则

1. **所有数据必须标注具体来源**
   - 不能只写"根据市场数据"，要写"根据香港保监局2025年数据"
   - 不能只写"机构上调目标价"，要写"高盛于2026年5月上调友邦目标价至120港元"
   - 具体到：机构名、时间、数据值

2. **原文数据要保留，换表达方式**
   - 原文："友邦连续12年香港第一"
   - 重写后："根据香港保监局最新数据，友邦已连续12年位列香港新造保单总保费第一名"（保留数据，换表达）
   - 不能删除数据、不能模糊化数据

3. **数据格式规范**
   - 百分比要保留：新业务价值增长15%至55.16亿美元
   - 排名要保留：连续12年香港第一
   - 时间要保留：2025年10月入选D-SII名单
   - 对比数据要保留：市值大涨60%以上

---

## 工作流程（6步）

### STEP 0：确认文章角度（必先执行，不许跳步）

改写文章前，**必须先问蛮子想要哪个方向**，不能凭默认理解直接动笔。

常见方向选项：
- A. [具体方向A]
- B. [具体方向B]
- C. 其他（用户补充）

蛮子回复方向后，记录在任务里，然后才进入 STEP 1 写稿。

**⚠️ 禁止：** 蛮子还没选方向就开始写。

### STEP 1：抓取文章（仅公众号来源需要）

使用 `wechat-article-to-markdown-v2` 技能抓取文章内容：

```bash
python3 ~/.openclaw/workspace-customer-marketing/skills/wechat-article-to-markdown-v2/scripts/wechat_to_md.py "<URL>" -o "/tmp/wechat_articles"
```

### STEP 2：拆解文章热门结构 + 爆款要素 + 仿写全文

1. 拆解原文结构（选题切入/核心观点/论证逻辑/结尾方式）
2. 提取爆款要素（哪句话/哪个观点最吸引人）
3. **标注所有数据及其来源**
4. 仿写完整全文（保持原意，但更符合传播逻辑）

### STEP 3：Claire风格重写 + 生成四件套

**Claire风格特征：**
- 沉稳、有深度、接地气、不装逼
- 财富管理专业人士应有的调性
- 像朋友聊天，不打官腔
- 有思考深度但不教条

**四件套内容：**
1. **标题选项（3选1）** — 吸引点击、有记忆点
2. **推荐摘要（≤120字）** — 让人一眼想读
3. **朋友圈文案（3条）** — 不同角度、可直接用
4. **文生图提示词** — 每篇文章生成配图提示词（蛮子在豆包生成）

**Claire品牌配图标准结构（5张图）：**

| 序号 | 图片位置 | 命名 | 风格定位 |
|------|---------|------|---------|
| 1 | 文章最开头（片头） | `header.jpg` | 温暖场景隐喻，情绪引导，不是数据 |
| 2 | 封面图 | `cover_v2.jpg` | 大字排版typography，编辑感留白，简约不冰冷 |
| 3 | PART 01 配图 | `part01_v2.jpg` | 手绘信息卡，数据+图标隐喻，温暖不警报 |
| 4 | PART 03 配图 | `part03_v2.jpg` | 手绘信息卡，2×2网格逻辑图 |
| 5 | 文章结尾（片尾） | `footer.jpg` | 温情收尾，呼应主题，无CTA压迫感 |

**配图提示词生成规范：**
每篇文章生成 1张封面图 + N张章节配图，通用公式：
```
创作一张手绘风格的信息图卡片，比例为 16:9 横版。
背景为带有纸质肌理的米色，营造质朴氛围。
卡片上方用红黑相间的大号毛笔草书字体书写「[章节主题]」。
文字内容以中文草书分[数字]小节呈现...
```

**双语气泡卡制作流程（2026-06-06 已验证）：**
引言卡片需出英文原句 + 中文翻译两个版本，Midnight Ink 黑金风格：
1. 用 `write_file` 将 HTML写入 `/tmp/<slug>/index-en.html`（英文版）和 `/tmp/<slug>/index-zh.html`（中文版）
2. 用 `terminal` + Playwright 对每个 HTML 截图：`page.$('#card-id'); el.screenshot(...)`
3. 英文版先出，确认排版OK后再复制生成中文版（结构完全一致，只改文字）
4. 发送顺序：EN版 → 确认 → ZH版 → 发飞书给蛮子

**配图工具规则（2026-06-05 确认，已更新2026-06-06）：**
- **fal.ai / image_generate 已禁用**（不论任何情况，不再调用）
- **guizang-card-skill HTML + Playwright 截图 = 唯一路径**
- 蛮子在豆包/即梦生成后发给我，我负责上传推送
- 中文金句卡片底部品牌栏格式：
  ```
  公众号：不躺平的钱          Claire CHEN
  ```
  用 HTML + Playwright 渲染时，在 `.content` 下加 `.brand-strip` div（高度96px，金色上边框，账号左/名字右）。

### STEP 3b：文章含金句时，生成配套金句卡片（2026-06-06 新增）

**判断标准：** 文章有≥3句值得单独成卡的引用句时，自动触发，无需用户要求
**卡片数量：** 1张/句，最多不超过5张
**风格：** Midnight Ink 黑金风格（理财/财富类内容专用）
**工具：** guizang-card-skill 的「文章金句卡片模式」

**工作流：**
1. 写文章时标注每句金句的"出现位置"（章节）
2. 写完文章+四件套后，**主动生成金句卡片**并随文章一起发飞书确认
3. 蛮子确认后，配图和文章一起手动插入草稿箱

**⚠️ 不要等用户要求。** 有金句的文章，金句卡片是标准输出的一部分，用户说"写得好多了"意味着内容方向已确认，此时应主动生成卡片附上。缺少卡片是输出不完整，不是用户没要求。

---

### STEP 4：存入本地文件备份

文件：
- `{标题}_原文.md` — 抓取的原文
- `{标题}_CLAIR版.md` — Claire风格重写版（含四件套）

**配图路径存放：** `~/.openclaw/workspace-customer-marketing/gongzhonghaoneirong/{系列}/{标题}/配图/`

### STEP 5：飞书确认 → 推送草稿箱

**⚠️ 草稿推送流程（2026-06-02确认）：必须先飞书确认，再推草稿箱**

蛮子的工作流有两步：
1. **第一步**：内容先发飞书给蛮子确认（`target: feishu:ou_72dbf7598ab4270ed7f5180bf41fd689`）
2. **第二步**：蛮子确认OK后，再推送草稿箱

**依赖技能 - urllib 推送草稿（避免 requests 乱码）：**

```python
import urllib.request, json

APPID = 'wx37f93a23f90770b4'
APPSECRET = 'c5fc89db461f4de7d55b65091979ce66'
r = urllib.request.urlopen('https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + APPID + '&secret=' + APPSECRET)
TOKEN = json.loads(r.read())['access_token']

article = {
    'title': '文章标题',
    'author': '环球经纪人Claire',
    'digest': '摘要',
    'content': '<p>正文HTML</p>',
    'thumb_media_id': '<封面图media_id>',
    'need_open_comment': 1,
    'only_fans_can_comment': 0
}

payload = json.dumps({'articles': [article]}, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    'https://api.weixin.qq.com/cgi-bin/draft/add?access_token=' + TOKEN,
    data=payload,
    headers={'Content-Type': 'application/json; charset=utf-8'}
)
r2 = urllib.request.urlopen(req)
result = json.loads(r2.read())
print(result)
```

**关键点：**
- `ensure_ascii=False` → 保持UTF-8中文不转义
- `.encode('utf-8')` → 直接发送UTF-8字节
- `urllib.request.Request` → 直接控制请求体编码

**获取 thumb_media_id（必须用 add_material，不能用 media/upload）：**
```bash
curl -s -F "media=@/tmp/cover.jpg" \
  "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${TOKEN}&type=thumb"
# 返回 media_id 格式：XDSxRVK2ZHBjglHZA5gSc...（固定长度，非 x 开头）
```

---

## 数据保留检查清单

重写完成后，自查以下数据是否已保留：

- [ ] 机构名称 + 具体目标价/评级
- [ ] 时间节点（如"2025年10月"、"过去一年"）
- [ ] 百分比数据（增长率、收益率等）
- [ ] 排名数据（"连续12年第一"）
- [ ] 金额数据（55.16亿美元、120港元等）
- [ ] 数据来源标注（香港保监局、高盛、瑞银等）

---

## 已知Bug与修复记录

### Bug：草稿内容乱码（Unicode 转义序列）

问题：推送到草稿箱的文章，正文显示为 `\u53cb\u90a6...` 而不是正常中文

根本原因：requests.post(url, json={'articles': [...]}) 时，中文被转为 Unicode 转义序列

**修复方案：** 改用 urllib.request.Request + json.dumps(ensure_ascii=False).encode('utf-8')（见 STEP 5 代码）

### Bug：IP 不在白名单（40164/40001）

诊断：先查服务器 IP `curl -s ifconfig.me`，确认是否已加入微信公众平台 IP白名单

当前服务器 IP：111.229.192.217

### Bug：草稿 thumb_media_id 无效（40007）

根本原因：thumb_media_id 需要**永久素材**（通过 add_material 接口上传）的 media_id，不能用 media/upload 的临时 media_id

正确流程：用 curl 上传图片到 add_material 接口获取永久素材 media_id

---

## 知识管理规范（蛮子工作流，2026-06-03确立）

### 信息三层分类

| 信息类型 | 存储位置 | 例子 |
|---------|---------|-----|
| TO DO、进行中的任务、做一半的session | `~/.hermes/task.md` | 今日任务清单、文章写到一半 |
| 配置/凭证/API/数据库ID | `~/.hermes/secret&API.md` | Notion Token、微信公众号凭证 |
| 核心事实、用户偏好、长期规则 | memory | 蛮子风格偏好、发布规则 |

**规则：找不到API/凭证 → 先搜 `~/.hermes/secret&API.md`，搜不到再问蛮子。**

---

## 使用示例

**用户输入：** `https://mp.weixin.qq.com/s/xxxxx`

**AI 自动执行：**
1. 抓取文章
2. 拆解+仿写（保留所有数据及来源）
3. Claire风格重写+四件套
4. 存入本地文件备份
5. 发飞书给蛮子确认
6. 蛮子确认后，用 urllib 推送到公众号草稿
