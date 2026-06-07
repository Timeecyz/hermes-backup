---
name: wechat-article-writing
description: 微信公众号文章生成+发布工具（WAW）。触发词：WAW、写公众号、生成公众号文章、公众号改写、生成引流文章、生成配图、文章转写、Claire风格文章、发布公众号。核心功能：生成文章→生成配图提示词→存Notion→推草稿箱，一条龙完成。
---

# 公众号文章改写+生成+发布 Skill（WAW）

> **触发规则**：当用户消息中包含"写公众号"、"生成公众号文章"、"WAW"、"发布公众号"等关键词时，自动启用本技能。

将微信公众号文章快速转化为符合 Claire CHEN 风格的爆款引流公众号文章，配套生成配图提示词，**自动推送到微信草稿箱**，一条龙完成。

---

## ⚡ 自动执行流程（零配置启动）

> **⚠️ CRITICAL PITFALL: Never write a bare article body**
>
> The #1 mistake is delivering only the article body without the full 15-module Claire structure.
> **When in doubt, ALWAYS load this skill FIRST before writing.**
> The skill defines the complete output shape — skipping it means missing the header, footer, 4-step deliverables, and prompts that the user expects.
>
> This skill was actively consulted mid-session and the agent still omitted the Claire 15-module structure. That failure mode is now hard-coded as a mandatory gate below.

## ⚡ 自动执行流程（零配置启动）

**Before writing ANY article, always load this skill first.** The skill defines the complete output shape.

```python
# First: load the skill
skill_view(name="wechat-article-writing")
```

**Then execute the full pipeline:**

```
1. 识别主题 → 2. 搜索数据 → 3. 写文章（含完整15模块 Claire结构）
→ 4. 生成配图提示词 → 5. 保存到Notion
→ 6. 推送微信草稿箱 → 7. 输出四件套
```

---

### ⚠️ PITFALL: Notion API Block Append Endpoint

When appending blocks to a Notion page, the correct endpoint is **`blocks/{PAGE_ID}/children`** (NOT `pages/{PAGE_ID}/blocks`). The latter returns `invalid_request_url`.

Workaround: connection resets are common on bulk block writes. Use batched writes (4 blocks per batch) with retry logic (3 attempts, 1s sleep between batches).

---

## 📥 输入方式

支持三种方式，任意一种即可启动：

| 方式 | 说明 | 示例 |
|------|------|------|
| 甩链接 | 直接丢公众号原文链接 | `帮我写公众号：https://mp.weixin.qq.com/s/xxx` |
| 甩主题 | 描述需求，我搜索+写 | `写一篇关于HIBOR的科普公众号` |
| 甩关键词 | 简短关键词启动 | `写公众号：世代悦享3` |

---

## 📊 数据搜索规范（必须执行！）

### 搜索要求

**每次写文章前，必须搜索最新数据！**

| 步骤 | 操作 | 要求 |
|------|------|------|
| 1 | 搜索核心主题数据 | 至少2个权威来源（官网、监管机构、主流财经媒体） |
| 2 | 提取关键数据 | 数字、百分比、对比数据必须标注来源 |
| 3 | 标注数据来源 | 正文内嵌格式 + 文末数据来源专区 |

---

## 📝 文章输出规范（15模块 + 强制结尾四件套）

### Claire CHEN 固定15模块格式

| 序号 | 模块 | 说明 |
|------|------|------|
| 1 | 自我介绍 | 💡 Claire CHEN 固定开头 |
| 2 | 公众号名片 | 欢迎关注，一起守住财富 |
| 3 | 推荐关注 | |
| 4 | 上期回顾 | 系列文章引流上期（可选） |
| 5 | 问题引入 | 读者疑问切入 |
| 6 | 正文 | PART 01/02/03... 分节，数据有来源标注 |
| 7 | 写在最后 | 行动建议 + 风险提醒 |
| 8 | 下期预告 | 系列文章才有 |
| 9 | 公众号名片 | 重复出现加强印象 |
| 10 | 互动引导 | 点赞/留言/分享 |
| 11 | 往期推荐 | 3-5篇相关文章 |
| 12 | 名片图片 | **此处插入图片：名片** |
| 13 | 风险提示 | 声明文字 |
| 14 | 喜欢作者 | 赞赏引导 |
| 15 | 作者署名 | 环球经纪人Claire |

---

### 🖼️ 配图插入标记规范（强制！）

| 用途 | 插入标记 | 比例 |
|------|---------|------|
| 封面图 | **此处插入图片：封面-fengmian** | 2.35:1 |
| 数据/信息图 | **此处插入图片：数据图-序号** | 16:9 |
| 对比图 | **此处插入图片：对比图-序号** | 16:9 |
| 总结图 | **此处插入图片：总结图** | 16:9 |
| 风险提示图 | **此处插入图片：风险图** | 16:9 |
| 名片图 | **此处插入图片：名片** | 1:1 |

---

## 🚨 蛮子公众号封面规范（必须遵守！）

### 默认风格：Midnight Ink 深色暖金（2026-06-03起）

蛮子确认：以后所有公众号封面默认用 **Midnight Ink 深色暖金**，无需再问。

**配色：**
| 元素 | 色值 |
|------|------|
| 背景 | `#0e0d0c` (深黑) |
| 强调色 | `#d4a04a` (暖金) |
| 文字 | `#ece2cf` (米白) |
| 次要文字 | `rgba(236,226,207,.40-.55)` |

**Midnight Ink 的 ONLY official dark Editorial 配色，不能用其他深色变体。**

### 封面图比例（微信标准）
| 用途 | 比例 | 尺寸 |
|------|------|------|
| 封面图（消息列表） | 2.35:1 | 940×400px |
| 封面图（转发卡片） | 1:1 | 1080×1080px |

### 封面图生成工具
- 子 Agent：`guizang-social-card-skill`，theme=`midnight-ink`
- 输出 21:9 (2100×900) + 1:1 (1080×1080) 配对封面
- 蛮子确认后再用

---

### 蛮子文章发布流程（必须遵守！）

1. 文章写完后，**先发飞书给蛮子确认**，不直接推送草稿箱
2. 蛮子确认OK后，才走 wenyan-cli 推送或手动粘贴草稿箱
3. 配套4件套（封面图Prompt+摘要+爆款标题+朋友圈转发内容）要一起给她
4. 发飞书用 `send_message`，target: `feishu:ou_72dbf7598ab4270ed7f5180bf41fd689`

### 蛮子文章改写偏好
改完后直接飞书发给她，不走草稿箱推送。她看完确认后再更新草稿箱。

---

### 2. 获取微信读书 API Key（必须先查 secret&API.md！）

**蛮子明确要求：不要问，先查。**

查 `~/.hermes/secret&API.md`，找 `微信读书` 部分：
- 有 key → 直接用（环境变量 `WEREAD_API_KEY=wrk-xxxx`）
- 没 key → 用公开信息整理核心内容存 Notion，callout 标注「微信读书API未配置，暂无个人划线笔记，后续补充」

### 3. 生成封面图

**默认风格：Midnight Ink 深色暖金（2026-06-03起）**

蛮子确认：以后所有公众号封面默认用 **Midnight Ink 深色暖金**，无需再问。

**配色：**
| 元素 | 色值 |
|------|------|
| 背景 | `#0e0d0c` (深黑) |
| 强调色 | `#d4a04a` (暖金) |
| 文字 | `#ece2cf` (米白) |
| 次要文字 | `rgba(236,226,207,.40-.55)` |

**封面图比例（微信标准）**
| 用途 | 比例 | 尺寸 |
|------|------|------|
| 封面图（消息列表） | 2.35:1 | 940×400px |
| 封面图（转发卡片） | 1:1 | 1080×1080px |

**封面图生成工具：** 子 Agent 调用 `guizang-social-card-skill`，theme=`midnight-ink`，输出 21:9 + 1:1 配对封面，蛮子确认后再用。

**配图比例：**
| 用途 | 比例 |
|------|------|
| 封面图（消息列表） | 2.35:1 |
| 封面图（转发卡片） | 1:1 |
| 数据图/信息图 | 16:9 |

---

## 📦 存档与Notion保存

### 文章目录结构

```
gongzhonghaoneirong/{系列}/{序号-中文描述}/
├── 公众号文章.md              # 完整文章（含所有标记）
├── 配图提示词.md             # 所有配图的AI生成提示词
├── 公众号推荐概要.md          # 120字推荐概要
├── 朋友圈转发文案.md          # 3条朋友圈文案
├── 00-fengmian.png           # 封面图（消息列表 2.35:1）
├── 00-fengmian-card.png       # 封面图（转发卡片 1:1）
├── 01-xxx.png                # 数据图（16:9）
├── 02-xxx.png                # 信息图（16:9）
└── 03-xxx.png                # 总结图（16:9）
```

### Notion保存（公众号内容库）

文章完成后，将以下内容存入 Notion 公众号内容库（ID: `34acd9aa-41cc-818f-aae0-c6ce9e77036f`）：

| 字段 | 内容 |
|------|------|
| 名称 | 文章标题 |
| 状态 | 草稿/待发布/已发布 |
| 类型 | 系列/热点/科普/产品解析 |
| 标签 | 根据主题打标签 |
| 配图 | 封面图文件 |
| 发布日期 | 计划发布日期 |
| 负责人 | Claire CHEN |

---

## 🔥 微信草稿箱推送流程

### 第一步：获取Access Token

```python
APPID = 'wx37f93a23f90770b4'
APPSECRET = 'c5fc89db461f4de7d55b65091979ce66'
r = requests.get('https://api.weixin.qq.com/cgi-bin/token', params={
    'grant_type': 'client_credential', 'appid': APPID, 'secret': APPSECRET
})
TOKEN = r.json()['access_token']
```

**服务器出口IP白名单：** `43.162.90.214`（需在微信公众平台后台添加）

### 第二步：上传封面图（永久素材）

```python
from PIL import Image, ImageDraw
import io

# 生成封面图（深蓝+金色主题，比例2.35:1）
img = Image.new('RGB', (940, 400), '#1a3a5c')
d = ImageDraw.Draw(img)
# 添加标题文字...
buf = io.BytesIO()
img.save(buf, 'PNG', quality=85)
buf.seek(0)

# 上传为永久素材
r2 = requests.post(
    f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={TOKEN}&type=image',
    files={'media': ('cover.png', buf, 'image/png')}
)
THUMB_MEDIA_ID = r2.json()['media_id']
```

### 第三步：MD转WeChat HTML

### 第四步：推送到草稿箱（⚠️ 必须用 urllib，不能用 requests）

**⚠️ 重要：requests.post 的 json= 参数会导致中文乱码（变\u转义），必须换用 urllib**

```python
import urllib.request, json

# token 获取、封面上传用 requests（没问题）
# 推送草稿必须用 urllib！

article = {
    'title': '微信标题（≤11字）',
    'author': 'Claire',
    'digest': '摘要（≤27字，勿超）',
    'content': html_content,
    'thumb_media_id': THUMB_MEDIA_ID,
    'need_open_comment': 1,
    'only_fans_can_comment': 0,
}

# ✅ 正确方式
payload = json.dumps({'articles': [article]}, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    'https://api.weixin.qq.com/cgi-bin/draft/add?access_token=' + TOKEN,
    data=payload,
    headers={'Content-Type': 'application/json; charset=utf-8'}
)
r3 = urllib.request.urlopen(req)
result = json.loads(r3.read())
print(result)  # {'media_id': '...', 'item': [...]}

# ❌ 错误方式：requests.post + json= 会导致乱码
# r3 = requests.post(url, json={'articles': [article]}, headers={...})
```

---

## ✅ 结尾四件套（自动输出！）

### 1. 爆款标题（3个供选择）

| # | 标题 | 风格 |
|---|------|------|
| A | {标题A} | {风格描述} |
| B | {标题B} | {风格描述} |
| C | {标题C} | {风格描述} |

### 2. 公众号推荐概要（≤120字）

{一段话概括文章核心内容}

### 3. 朋友圈转发文案（3条选择）

### 选项1：痛点切入型
---
{pain point}
{core message}
💡 {highlight 1}
💡 {highlight 2}
👉 {cta}
#保险科普 #香港保险 #财富管理

---

### 选项2：数字冲击型
---
{numbers/phenomenon}
{interpretation}
✨ {highlight 1}
✨ {highlight 2}
{interaction}
#港险新知 #{topic}

---

### 选项3：互动提问型
---
{question that prompts thinking}
{professional answer}
你们觉得呢？留言聊聊 👇
{topic tags}

---

## 🎨 配图提示词生成规范

**手绘草书风规范：**
- ✅ 纸质肌理米色/米白色背景，温暖手工质感
- ✅ 红色/黑色大号毛笔草书字体
- ✅ 中文草书，流畅韵律感，清晰可读
- ✅ 2-4个清晰小节，每节简短精炼
- ✅ 简单有趣的手绘图标
- ✅ 充足留白空间
- ❌ 冰冷金融图表、写实风格、高科技感

| 序号 | 类型 | 比例 | 必须性 |
|------|------|------|-------|
| 01 | 封面图 | 2.35:1 | 必须 |
| 02 | 数据图 | 16:9 | 每个核心数据点 |
| 03 | 信息图 | 16:9 | 每2-3个要点 |
| 04 | 总结图 | 16:9 | 结尾行动建议 |
| 05 | 风险图 | 16:9 | 风险提示区块 |
| 06 | 名片图 | 1:1 | 作者署名区 |

---

## 📌 合规底线（绝对禁止突破）

- ❌ 不承诺收益
- ❌ 不保证理赔
- ❌ 不虚构数据
- ❌ 禁止"保本""稳赚""零风险"等违规表述
- ✅ 分红产品必须区分"保证收益"与"非保证收益"
- ✅ 跨境保单必须提示：监管、汇率、税务、法律适用

---

## 🚀 执行检查清单

- [ ] 识别到"写公众号"触发词
- [ ] 已搜索主题相关权威数据（≥2个来源）
- [ ] 文章包含 Claire 15模块
- [ ] 关键数据有来源标注
- [ ] 文末有数据来源专区
- [ ] 配图位置有明确标记
- [ ] **已推送到微信草稿箱**
- [ ] **已保存到Notion公众号内容库**
- [ ] 文章结尾有四件套
- [ ] 已生成配图提示词

---

## 附录：蛮子内容存储决策指南

> 见 `references/memory-vs-skill.md` — 存 memory 还是存 skill 的判断标准，蛮子自述原则。

## 附录：公众号文章工具链（wechat-article-search 内容摘要）

> `wechat-article-search` 已合并至此技能，此处保留摘要便于直接查用。

### 搜索功能

当用户需要查找微信公众号文章时：

1. **确认关键词** — 用户提供的搜索词
2. **执行搜索** — `node scripts/search_wechat.js "关键词"`
3. **返回结果** — 标题、摘要、发布时间、公众号名称、可访问链接

### 依赖
```bash
npm install -g cheerio
```

### 场景
- 用户说"搜某个关键词的公众号文章"
- 需要快速获取：标题、摘要、发布时间、公众号名称、链接

### wechat-article-to-markdown 补充说明

微信公众号文章转 Markdown（`mp.weixin.qq.com` 链接）时：

- 移动端渲染（iPhone Safari UA + 393×852 viewport）
- 支持临时分享链接（tempkey）正常渲染
- 懒加载图片需滚动触发 `data-src`

使用 `wechat-article-to-markdown-v2` 技能获取完整转换流程。