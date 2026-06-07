---
name: gao-neng-liang-girl-wechat-editorial
description: 「高能量女孩日记」公众号配图编辑规范——墨绿暖调（sage green）风格。从文章内容提取到配图组生成、推送草稿箱的全流程。适用于用户要求"墨绿系"、"sage green"风格时触发。
tags: wechat, social-card, editorial, sage-green, high-energy-girl
version: "1.0.0"
icon: 🌿
os: linux, macos
---

# 高能量女孩日记 · 墨绿暖调配图编辑规范

> 来源：2026-06-04 首次验证 | 文章「Do less.」配图组

## 触发条件

- 用户提到「高能量女孩日记」公众号配图
- 用户选择墨绿/sage green/sage-leaf 风格
- 用户要求 guizang 风格且未指定具体主题

---

## 墨绿暖调色板（Sage Green Editorial）

### CSS 变量（直接使用）

```css
:root {
  --paper:      #f3f4ef;   /* 淡米绿底 · warm sage cream */
  --paper-2:    #e2e8d8;   /* 浅墨绿 · light sage */
  --ink:        #1c2e1c;   /* 深墨绿 · deep forest */
  --muted:      #5d6b5a;   /* 灰墨绿 · muted sage */
  --line:       rgba(28,46,28,.20);
  --accent:     #4a6741;   /* 鼠尾草绿 · sage olive */
  --accent-soft:#d4dfcc;
}
```

### 字体规范

| 角色 | 字体 | 字重 | 说明 |
|------|------|------|------|
| 显示标题 | Noto Serif SC | 400-500 | 衬线中文，大字号 |
| 正文 | Noto Sans SC | 300-400 | 无衬线中文 |
| 标签/元数据 | Inter / IBM Plex Mono | 600 | 大写字母间距 |

### 视觉锚点

- **色调**：淡米绿底 + 深墨绿字 + 鼠尾草绿强调，暖调沉稳，有深度
- **不要**：纯白底、深黑字、冷蓝色调、数据图表感
- **配图气质**：编辑感、文学气质、有温度，不教条

---

## 配图组结构（标准5张）

| 序号 | 图片位置 | 命名规则 | 尺寸 | 布局 |
|------|---------|---------|------|------|
| 1 | 封面图 | `xhs-cover.png` | 3:4 1080×1440 | M01 Magazine Cover |
| 2 | PART 01 | `xhs-part01.png` | 3:4 1080×1440 | M08 Tall Ledger |
| 3 | PART 02 | `xhs-part02.png` | 3:4 1080×1440 | M05 Checklist |
| 4 | 结尾Banner | `xhs-closing.png` | 3:4 1080×1440 | M04 Pull Quote |
| 5 | 微信主封面 | `wechat-21x9.png` | 21:9 2100×900 | 左侧文字+右侧视觉 |
| 6 | 微信方封面 | `wechat-1x1.png` | 1:1 1080×1080 | 居中大标题 |

---

## 布局配方参考

### M01 Magazine Cover（封面）
- 顶部：分类标签 + 金色强调线
- 中心：大号衬线标题（2-3行）
- 底部：关键信息 strip

### M08 Tall Ledger（PART 配图）
- 标题 + 三个ledger行
- 每行：编号(mono) + 标题(serif) + 副标题(sans)
- 底部引言卡片

### M05 Checklist（原则型配图）
- 大号衬线标题
- 三个原则块（编号 + 标题 + 说明）
- 水平分隔线

### M04 Pull Quote（结尾）
- 居中大标题
- 引言 + 出处
- 底部元数据 strip

---

## 生成工作流

### Step 1：创建 HTML

路径：`/tmp/sage_green_article/index.html`

从 `guizang-social-card-skill` 的 `template-editorial-card.html` 出发，
设置 `data-theme` 对应的 CSS 变量。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600&family=Noto+Sans+SC:wght@200;300;400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Noto+Serif+SC:wght@300;400;500&display=swap">
  <style>
    :root {
      --paper:      #f3f4ef;
      --paper-2:    #e2e8d8;
      --ink:        #1c2e1c;
      --muted:      #5d6b5a;
      --line:       rgba(28,46,28,.20);
      --accent:     #4a6741;
      --accent-soft:#d4dfcc;
    }
    /* ... 其他样式 ... */
  </style>
</head>
```

### Step 2：截图导出

在 `hermes-agent` 目录下运行（该目录有 `node_modules/playwright`）：

```javascript
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const base = 'file:///tmp/sage_green_article/index.html';

  const sizes = [
    ['#cover', { width: 1080, height: 1440 }, '/tmp/sage_green_article/xhs-cover.png'],
    ['#part01', { width: 1080, height: 1440 }, '/tmp/sage_green_article/xhs-part01.png'],
    ['#part02', { width: 1080, height: 1440 }, '/tmp/sage_green_article/xhs-part02.png'],
    ['#closing', { width: 1080, height: 1440 }, '/tmp/sage_green_article/xhs-closing.png'],
    ['#wechat-21x9', { width: 2100, height: 900 }, '/tmp/sage_green_article/wechat-21x9.png'],
    ['#wechat-1x1', { width: 1080, height: 1080 }, '/tmp/sage_green_article/wechat-1x1.png'],
  ];

  for (const [id, vp, out] of sizes) {
    await page.setViewportSize(vp);
    await page.goto(base + id);
    await page.waitForTimeout(600);
    await page.screenshot({ path: out, fullPage: false });
  }

  await browser.close();
})();
```

### Step 3：飞书发送预览

```
send_message → MEDIA:/tmp/sage_green_article/xhs-cover.png
```

分条发送，让蛮子逐张确认。

### Step 4：确认后存档

```bash
mkdir -p ~/.openclaw/workspace-customer-marketing/gongzhonghaoneirong/高能量女孩日记/{标题}/
cp /tmp/sage_green_article/*.png ~/.openclaw/workspace-customer-marketing/gongzhonghaoneirong/高能量女孩日记/{标题}/
```

---

## 关键注意事项

- **sage green 暖调**：不是冷色调翠绿，是带米色底的暖墨绿
- **衬线标题**：M01/M08/M04 必须用 Noto Serif SC，不能用 sans
- **引言格式**：`border-left: 4px solid var(--accent)` + 斜体 serif
- **ledger 编号**：mono 色用 `--accent`，字号 20px
- **正文不要纯白底**：Editorail 要求有 atmosphere layer（grain + paper-wash）

---

## 相关技能

| 技能 | 用途 |
|------|------|
| `guizang-social-card-skill` | 生成 HTML 配图组的核心 skill |
| `wechat-article-writing` | 「高能量女孩日记」写作风格规范 |
| `gao-neng-liang-girl-wechat` | 内容策略（选题/系列规划） |
| `wechat-article-rewriting-clairestyle` | 「不躺平的钱」编辑规范（对比参考） |