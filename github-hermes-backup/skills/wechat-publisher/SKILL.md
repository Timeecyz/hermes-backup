---
name: wechat-publisher
description: "一键发布 Markdown 到微信公众号草稿箱。基于 wenyan-cli，支持多主题、代码高亮、图片自动上传。"
---
name: wechat-publisher
description: "微信公众号草稿箱文章推送。当蛮子说「推送文章」「发布草稿」「微信公众号」时触发。"
metadata:
  {
    "openclaw":
      {
        "emoji": "📱",
      },
  }
---

# wechat-publisher

**微信公众号草稿箱文章推送**

当蛮子说「推送文章」「发布草稿」「微信公众号」时使用。

## 完整工作流（视频配套文章场景）

当蛮子说「写视频脚本」并要求配套公众号文章时，执行以下流程：

**第一步：写视频脚本 + 配套文章**
- 视频脚本（85秒口播版）：开场钩子 + 3个维度 + CTA结尾
- 配套公众号文章（长文版）：同主题深度展开，增加细节、数据、场景
- 同时输出4件套：
  1. **封面图Prompt**：凹版版画风格 + 具体场景描述
  2. **100字摘要**：用于发布时填写摘要字段
  3. **爆款标题3选1**：A/B/C选项，格式为《标题全文》
  4. **朋友圈转发内容**：100字左右，带话题标签

**第二步：发飞书给蛮子确认**
- 脚本 + 配套文章 + 4件套 一起发
- 等蛮子反馈，确认方向OK后再推进

**第四步：存Notion**
- 每篇文章存为独立页面（在「不躺平的钱」数据库）
- 页面内容包含：视频脚本 + 配套文章全文 + 4件套
- 4件套单独追加到页面底部（heading_2「📋 4件套」+ 各heading_3小节）

**第五步：发飞书给蛮子确认**
- 脚本 + 配套文章 + 4件套 一起发
- 蛮子偏好：看完确认后手动复制到公众号草稿箱（不走wenyan-cli推送）

**蛮子文章发布流程（已验证，2026-06-02）：**
1. 我写完文章 + 4件套 → 发飞书给蛮子
2. 蛮子确认OK → 手动复制到公众号草稿箱
3. 不走 wenyan-cli 推送（因为无法直接操作）

所以当蛮子说「存公众号草稿」时：
- 如果文章已写好 → 直接发飞书给她确认
- 如果需要自动化推送 → 需要先拿到 AppID+AppSecret 配置wenyan-cli

---

## 两种状态 — 处理逻辑不同

### 状态A：文章已在草稿箱（内容已就位）
**这是最常见场景**——文章已经在草稿箱，只需要发布。

蛮子的工作流：
1. 内容写入草稿箱
2. 我帮她检查是否还有第二篇待发
3. 由蛮子在公众号后台手动发布

**直接问蛮子：草稿箱里今天要发哪篇？还有第二篇吗？**
不需要我生成内容，只需要确认+推送。

### 状态B：需要从零写文章并推送（完整流程）
走 wechat-article-writing 或 wechat-article-rewriting-clairestyle skill。

## 凭证配置（ Wenyan-CLI 方式）

> ⚠️ **凭证不在系统里** — 需要蛮子提供。wenyan-cli 发布需要 AppID + AppSecret。

**获取方式：**
微信公众号后台 → 设置与工具 → 公众平台设置 → 基本配置 → AppID / AppSecret

**配置步骤（拿到凭证后）：**
```bash
export WECHAT_APP_ID=your_app_id
export WECHAT_APP_SECRET=your_app_secret
wenyan publish -f article.md -t lapis
```

**wenyan-cli 安装（Linux 服务器）：**
```bash
npm install -g @wenyan-md/cli --unsafe-perm
# 如果权限报错，尝试：
sudo npm install -g @wenyan-md/cli
```

**IP 白名单：** 确保服务器 IP 已添加到微信公众号后台 → 开发 → 基本配置 → IP 白名单

### 凭证查找顺序
1. 先搜索 ~/.hermes 内是否有 wx{a-z0-9]{16} 模式的AppID
2. 搜索不到再问蛮子要
3. 蛮子提供后存入 ~/.hermes/.env

## 文章查找（当蛮子说"昨天两篇"时）

**搜索位置：** 微信公众号草稿箱（公众号后台）

**搜索步骤：**
1. 直接用 WeChat Draft API 读取草稿箱（见 `references/wechat-draft-api.md`）
2. 根据标题或关键词定位文章，获取 media_id
3. 用 media_id 获取完整 HTML 内容
4. 如需要更新封面图，生成后上传到草稿箱

**参考：** `references/wechat-draft-api.md` — 包含完整的 Python 操作模板和已知坑

---

## 蛮子工作流（已验证 2026-06-05）

1. 用 Draft API 读取草稿箱 → 定位文章 → 获取 HTML 内容
2. 分析内容 → 生成配图提示词（Midnight Ink 深色暖金风格）
3. **发飞书给蛮子确认**（不走 wenyan-cli）
4. 蛮子确认后手动复制到公众号草稿箱

---

## 参考资料

```markdown
---
title: 文章标题（必填！）
cover: ./assets/cover.jpg  # 必填！可用相对路径或网络URL
---

正文...
```

**title 和 cover 都是必填字段，缺一不可。**

## API 已知限制（2026-06-06 验证）

**核心结论：微信API设计为"更新已有草稿"，不是"创建并设封面"。完整自动化推送不可行，实际用"发飞书+手动粘贴"。**

### 三个必须知道的坑

**① thumb_media_id 必须是草稿箱里已有的 XDSx... 前缀ID**
新上传的图片返回 f61mr... 前缀 media_id，不能用作封面图 thumb_media_id，会报 40007 invalid media_id。
→ 封面图必须先在微信后台手动上传到草稿箱，拿到 XDSx... ID后再用API更新内容。

**② 封面图必须 < 64KB**
超过报 40006 invalid media size。
→ PIL压缩：`Image.open('cover.png').convert('RGB').resize((900,386), Image.LANCZOS).save('cover_thumb.jpg', 'JPEG', quality=70, optimize=True)`

**③ 正文图片上传必须用 requests.files{}**
urllib.request 报 41005 "media data missing"。
→ Python: `requests.post(upload_url, files={'media': ('image.png', img_data, 'image/png')})`

**④ execute_code 执行含中文HTML正文会 SyntaxError**
`execute_code` 的 code 参数对含中文嵌套引号的多行 Python 代码会报错（SyntaxError: invalid syntax）。
→ 正确做法：写脚本到 `/tmp/push_draft.py` → 用 `terminal` 执行。
→ 禁止：在 execute_code 的 code 字符串里直接写含中文和双引号嵌套的 HTML 正文。
→ 此坑命中两次（2026-06-06）：中文摘要含双引号 + HTML 正文含双引号，都是同样死法。

**⑤ 永久素材上传（add_material）必须用 urllib multipart**
之前误以为 requests.files{} 用于草稿图片上传，实际测试结果：
- `requests.post(url, files={})` → 临时素材上传（返回 f61mr... 前缀）用于正文图片
- `urllib + multipart/form-data` → 永久素材上传（返回 XDSx... 前缀）用于封面图 thumb_media_id
两种用途不同，不能互换。

**⑥ 带品牌栏的金句卡片生成流程（2026-06-06 验证）**
guizang-card-skill 可在卡片底部追加品牌 strip（HTML block + screenshot）：
```html
<div class="brand-strip">
  <span class="account">公众号：不躺平的钱</span>
  <span class="name">Claire CHEN</span>
</div>
```
执行顺序：生成 HTML → Playwright screenshot → 蛮子飞书确认 → 上传素材库（add_material）

---

## 蛮子工作流（已验证 2026-06-06）

1. 用 Draft API 读取草稿箱 → 定位文章 → 获取 HTML 内容
2. 分析内容 → 生成配图提示词（凹版版画风格）
3. **发飞书给蛮子确认**（不走wenyan-cli/API）
4. 蛮子确认后手动复制到公众号草稿箱，或用 API 推送（需先手动上传封面获取XDSxID）

**推荐路径：飞书确认 → 蛮子手动粘贴**（5分钟，比磕API快）

---

## 凭证存放位置

蛮子的凭证（如果提供）：
- 路径：`~/.hermes/.env`
- 变量名：`WECHAT_APP_ID` / `WECHAT_APP_SECRET`

## 参考资料
## 参考资料
- wenyan-cli: https://github.com/caol64/wenyan-cli
- wenyan 官网: https://wenyan.yuzhi.tech
- `references/material-upload-guide.md` — 永久素材上传 + 草稿推送完整代码（含中文HTML处理）
- `references/wechat-draft-api.md` — 完整 API 操作手册（含 token/草稿读写/正文图片上传）

