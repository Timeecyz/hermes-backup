# Guizang 配图生成 + 微信公众号草稿联动（2026-06-04）

> 本次验证了用 Guizang Social Card Skill 生成公众号配图的工作流。

## 触发条件

用户说"黑金风格"或选择 Guizang 风格时，自动调用本流程。

## 工作流

### 1. 生成 HTML 配图组

从 `guizang-social-card-skill` 的 `template-editorial-card.html` 或 `template-swiss-card.html` 出發，用 Midnight Ink theme（`data-theme="midnight-ink"`）。

参考文件：`/home/agentuser/.hermes/skills/guizang-social-card-skill/assets/template-editorial-card.html`

```bash
# 路径
/tmp/wechat_coverage_article/index.html   # 本次生成的HTML
/tmp/wechat_coverage_article/wechat-21x9.png   # 21:9 主封面
/tmp/wechat_coverage_article/wechat-1x1.png     # 1:1 方封面
/tmp/wechat_coverage_article/part01.png         # PART01 配图
/tmp/wechat_coverage_article/footer.png         # 片尾Banner
```

### 2. 截图导出各尺寸

使用 Node.js + Playwright（在 hermes-agent 目录下运行）：
```javascript
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 2100, height: 900 });
  await page.goto('file:///tmp/.../index.html');
  await page.screenshot({ path: '/tmp/.../wechat-21x9.png' });
  // 其他尺寸同理
  await browser.close();
})();
```

**注意：** Playwright 从 `/home/agentuser/.hermes/hermes-agent/` 目录运行（该目录下有 `node_modules/playwright`）。

### 3. 上传微信素材库

```bash
# 永久缩略图（草稿封面用 add_material，type=thumb）
curl -s -F "media=@/tmp/.../wechat-21x9.png" \
  "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${TOKEN}&type=thumb"

# 永久图片素材（内文配图用 add_material，type=image）
# ⚠️ 注意：media/upload 是临时素材（3天过期），add_material 是永久素材
# 内文配图必须用 add_material type=image，才能在素材库长期留存并手动插入正文
curl -s -F "media=@/tmp/.../part01.png" \
  "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${TOKEN}&type=image"
# 返回格式：{"media_id":"XDSxRVK2ZHBjglHZA5gSc...","url":"..."}
```

**⚠️ 草稿箱正文内嵌配图的限制：**
草稿箱不支持通过 API 在正文中嵌入通过 `media/upload` 上传的临时图片。
配图需用户手动从「素材库 → 图片」插入。
`add_material` 返回的 media_id 用于 `thumb_media_id`（封面），`media/upload` 返回的 media_id 只能用于临时展示，不能绑定到正文特定位置。

### 4. Midnight Ink Theme CSS 变量

```css
[data-theme="midnight-ink"] {
  --paper: #0e0d0c;
  --paper-2: #1a1714;
  --ink: #ece2cf;
  --muted: #9a8b75;
  --line: rgba(236,226,207,.22);
  --accent: #d4a04a;        /* 金色强调 */
  --accent-soft: #3a2a14;
}
```

### 5. 已知限制

- 草稿正文内图片：必须手动插入，API 无法自动嵌入
- Midnight Ink 配图背景是深色，正文排版要避免深色背景图覆盖文字的情况
- 内文表格：微信公众号对复杂表格渲染效果差，建议用 `<table style="border-collapse:collapse;">` 加内联样式，并确保字体不小于 14px