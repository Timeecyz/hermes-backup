---
name: guizang-social-card-skill
description: Generate Guizang-style social card image sets and WeChat official account cover pairs from articles, scripts, screenshots, product notes, subtitles, or photos. Use when the user asks for 小红书图文, Rednote/Xiaohongshu images, social cards, carousel images, 3:4 covers, 微信公众号封面, WeChat 21:9 + 1:1 covers, Swiss Style, or magazine-style social images.
---

# Guizang Social Card Skill

Create polished social card packages for Xiaohongshu/Rednote, WeChat Official Account, article covers, and platform thumbnails.

This skill is self-contained. It borrows visual principles from the Guizang PPT style system, but it must not edit the original PPT skill, its templates, or its references. If the original PPT skill is available, you may read it for reference only. Put all generated work in the current project or in the user-requested output folder.

## ⚠️ 配图工具硬规则（2026-06-05 蛮子确认）

- **fal.ai / image_generate 已禁用** — 不论什么情况，不再调用
- **guizang-card-skill HTML → Playwright 截图 = 唯一路径**
- 用户说"直接guizang生成"或"不要写Html图片直接发我" → 走 HTML + Playwright 截图路径，不要绕 fal.ai / image_generate
- 图片输出后用 `MEDIA:/path/to/file.png` 格式直接发给用户

## What To Produce

Use this skill for:

- Social card / carousel image sets: cover plus content pages, especially Xiaohongshu/Rednote 3:4.
- WeChat Official Account cover pairs: one `21:9` main cover plus one `1:1` square cover, composed together in the same HTML for visual checking.
- Screenshot-heavy product posts, article covers, tutorial carousels, outdoor/lifestyle notes, AI/product update explainers.
- Social images that need Guizang-style Swiss or editorial magazine layouts.

Do not use this skill for:
- Full slide decks or horizontal PPT websites. Use the PPT skill for that.
- Long-form video generation. Use a video skill for that.
- Pure image editing with no layout or article extraction requirement.

### Rednote Category Capability (capability circle)

The 11 most-common Rednote (小红书) categories fall into three buckets. See `references/category-cookbook.md` for the recipe-by-recipe routing.

**Strong end-to-end** (text, structure, and image story all in scope):

- 旅行 (Travel), 职场 (Workplace), 推荐 (Recommended, after specifying a subtype).

**Strong on text & structure; image needs to come from the user or a sourced library:**

- 游戏 (Game), 影视 (Film/TV), 美食 食谱方向 (Food — recipes only), 彩妆 教程方向 (Makeup — tutorials only), 健身 (Fitness), 家居 (Home), 穿搭 精选方向 (Outfit — capsule/essay only).

**Outside scope — push back honestly rather than promise a result:**

- 美食 菜品大片摆盘 (food-photography showcase).
- 穿搭 日常 OOTD 全身 (daily OOTD body shots; we cannot generate or simulate).
- 情感 梦核 / 氛围感装饰风 (dreamcore / aesthetic-light styling — clashes with both Editorial and Swiss).
- Y2K / 千禧辣妹 / 哥特萝莉 / kawaii decorated aesthetics.
- Pure photography showcase posts where the image is the entire deliverable.

When a request falls in the third bucket, name what we cannot do at intake — do not silently retrofit a layout that misses the user's intent.

## Core Principle

Expression comes first. The goal is not to squeeze text into posters; it is to turn the source into a clear visual argument.

For each page, decide:

- What should the viewer understand in one glance?
- What evidence, screenshot, or image supports it?
- Which words must be large, and which can become captions or metadata?
- What can be removed because it belongs in the post body, not the image?

## Required References

Read these files as needed:

- `references/platform-specs.md` for exact ratios, output sizes, and naming.
- `references/style-system.md` for Guizang editorial and Swiss visual rules.
- `references/theme-presets.md` when choosing electronic-magazine palettes or Swiss accent palettes.
- `references/layout-recipes.md` when selecting carousel/social-card/WeChat page structures.
- `references/components.md` for the shared component spec: font stacks, type scale, minimum readable sizes, Chinese title length bands, Swiss card-fill mutual-exclusion rule, image-container ratio classes, spacing tokens, and Lucide icon rules.
- `references/background-systems.md` when building electronic-magazine WebGL/ink/paper backgrounds.
- `references/portrait-fill.md` when adapting layouts to 3:4 and avoiding under-filled vertical space.
- `references/content-planning.md` for cover hooks, page breakdown, and copy compression.
- `references/production-workflow.md` for HTML/CSS rendering and image handling.
- `references/image-overlay.md` whenever text sits on top of a photo: photo qualification, localized tint fallback, and face / subject avoidance via multimodal subject mapping.
- `references/screenshot-treatment.md` when the user supplies an app / web / code / dashboard screenshot — picks `.frame-shot` over `.frame-img`, sets corners/shadow/bg/inset, decides on `.device-browser` or `.device-phone` chrome.
- `references/map-component.md` when the content has spatial relationships (travel route, store locations, walking tour) — real routes default to Mapbox Static or OSM static tiles; schematic SVG is only for conceptual / illustrative maps. Pins are HTML overlays; never use live JS maps.
- `references/title-shortener.md` when the task is a WeChat 21:9+1:1 cover pair, or any cross-platform reuse — derives the 1:1 short title from the long one (5-step extraction, 4 patterns, anti-patterns, sizing on `.poster.square`).
- `references/category-cookbook.md` to route a user-named Rednote category (旅行 / 职场 / 游戏 / 影视 / 彩妆 / 美食 / 穿搭 / 家居 / 健身 / 情感 / 推荐) to applicable recipes and to confirm scope.
- `references/qa-checklist.md` before delivering final images.

## Workflow

### 1. Intake

Gather only the missing information that changes the output:

- Target platforms and ratios.
- Source text, subtitles, article, or title.
- **Rednote category** — if the user names one of the 11 common types, route via `references/category-cookbook.md` to confirm inside capability circle. If outside-scope, surface that before designing.
- Supplied images/screenshots and where each should appear. **For News / Tutorial / Data / Review content, actively prompt for screenshots or photos** — they are the evidence layer.
- **If the user supplies only text (no images at all), ask once before designing:**

  ```
  这篇我需要 1-2 张图。三种走法：
  A. 你自己有照片 / 截图，传给我（推荐——最不"AI 感"）
  B. 我去 Pexels / Unsplash / Flickr 帮你找
  C. 用 AI 生成
  ```

  Recommend A in one line. Accept whatever the user picks and proceed. **Do not re-prompt later.** This question is one-shot.
- Preferred style if specified: Swiss Style, magazine/editorial, tech, outdoor, etc.
- Hard constraints: title text, no image on 1:1 cover, must include a hardware photo, keep screenshot readable, and so on.

If the user has already supplied enough context, proceed with reasonable assumptions.
If the content involves current product releases, policies, prices, claims, or news, verify unstable facts with browsing and cite sources in the final response.

### 2. Extract The Story

Turn the source into a page plan before designing.

For Rednote:

- Page 1 is the cover hook.
- Pages 2-N each carry one idea only.
- Use 5-9 pages for most posts. Compress or combine pages when lower areas become empty.
- Keep the post body for nuance; images should carry hooks, comparisons, checklists, and sharp takeaways.

For WeChat:
- Always produce a paired system: `21:9` main cover and `1:1` square cover.
- Build both covers in the same HTML file and add a combined preview section so their visual relationship can be checked together.
- `21:9` keeps the full or near-full title, subtitle, and one strong visual relation.
- `1:1` uses a simplified short title derived from the long title: big centered type, no image by default, no cramped subtitles.

### 3. Choose Style Mode

**Editorial Magazine x E-ink** brings:

- Serif/Songti display + quiet sans body, paper + ink palette.
- Atmosphere layer (paper grain / ink wash / WebGL canvas) over a warm paper base.
- Ledger rows, marginalia, pull quotes, large photo wells — magazine-feature feel.
- Best when you want the page to feel slow, considered, hand-set.

**Swiss International** brings:

- Inter / Helvetica feel, very light display at large sizes, mono labels at small.
- Strict left-aligned grid, hairline rules, one high-saturation accent.
- Card-fill matrices, KPI towers, h-bar charts, numbered statements — system / data feel.
- Best when you want the page to feel engineered, quantified, decisive.

If both feel viable, the question becomes editorial intent: "is this a feature story or a release note?" That decides the mode, not the topic itself.

Do not mix the two visual systems inside the same image set unless the user explicitly asks for a hybrid.

Then pick one theme:

- Editorial Magazine x E-ink uses one of 6 magazine palettes: Ink Classic, Indigo Porcelain, Forest Ink, Kraft Paper, Dune, or Midnight Ink.
- Swiss International uses one of 4 accent palettes: IKB Blue, Lemon Yellow, Lemon Green, or Safety Orange.

### 蛮子的配图风格要求

- 温暖、编辑感，typography-forward
- 不要金融图表感，不要冰冷数据堆砌
- 整体：手绘感/插画风，温暖色调（米色背景），炭笔黑+柔和强调色

### 黑金风格（Midnight Ink）适用范围 — 保险/理财内容专用（已确认2026-06-06）

黑金风格（深色底+金色强调）非常适合**保险/理财/财富管理**等沉稳专业的内容。黑金风格传达"高端、专业、有深度"的品牌调性——金融科普、退休规划、子女教育金、港险对比等主题完全可以优先选用 Midnight Ink。

**已验证场景：** "金钱的艺术"金句卡片系列（4张英文+4张中文+4张带品牌栏），Midnight Ink 风格完全合适。

**Midnight Ink 必须覆盖的背景层**：
```css
[data-theme="midnight-ink"] .grain {
  opacity: .26; mix-blend-mode: screen;
  background-image: radial-gradient(rgba(255,244,214,.10) 1px, transparent 1px);
}
[data-theme="midnight-ink"] .paper-wash {
  background:
    radial-gradient(80% 50% at 28% 16%, rgba(212,160,74,.12), transparent 64%),
    radial-gradient(70% 60% at 80% 86%, rgba(60,40,20,.20), transparent 72%),
    linear-gradient(180deg, rgba(236,226,207,.02), rgba(0,0,0,.32));
}
[data-theme="midnight-ink"] .frame-img {
  background: #18120f;
  box-shadow: 0 0 0 1px rgba(236,226,207,.10);
}
```
**若省略 grain + paper-wash 两层，深色卡片会糊成一团无法辨认。** 这三组 CSS 是 Midnight Ink 的必选配套，不可单独使用深色变量而省略背景层。

Read `references/theme-presets.md` for exact CSS tokens.

### 4. Plan Pages

Create a concise internal plan:

```text
Page 01 / cover / hook / image source / layout intent
Page 02 / point / key copy / visual evidence / layout intent
...
```

Use `references/layout-recipes.md` to choose page structures. Avoid making every page a repeated title-plus-card layout.

For 3:4 images, check `references/portrait-fill.md` before coding.

### 4.5. Copy The Seed Template

Do not write HTML from scratch. Pick one seed template based on the style mode chosen in Step 3:

- Editorial Magazine × E-ink → copy `assets/template-editorial-card.html` into the task folder as `index.html`.
- Swiss International → copy `assets/template-swiss-card.html` into the task folder as `index.html`.

The seed already wires up: font loading, theme tokens, all three poster sizes (`.poster.xhs` / `.poster.square` / `.poster.wide`), the pair-preview frame, grain/background layers, and all class definitions referenced by the layout recipes.

Set the theme/accent on the `<html>` element:

- Editorial: `<html data-theme="ink-classic | indigo-porcelain | forest-ink | kraft-paper | dune | midnight-ink">`.
- Swiss: `<html data-accent="ikb | lemon-yellow | lemon-green | safety-orange">`.

Replace the single placeholder poster after `<!-- POSTERS_HERE -->` with one `<section class="poster ...">` block per page, each carrying one Layout Recipe (M01-M16 for Editorial, S01-S12 for Swiss). Never load the wrong template's class system.

### 5. Build And Render

**Standard path (all cards):** HTML + Playwright screenshot.

- Create a task folder in the current workspace, e.g. `social-card-<slug>/`.
- Put source images in `assets/`.
- Start from the seed template copied in Step 4.5.
- Use Playwright to screenshot each `.poster` node:

```bash
cd /tmp && npm install playwright --save-dev  # 首次只需一次
cd /tmp && node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1080, height: 1440 });
  await page.goto('file:///path/to/index.html', { waitUntil: 'networkidle' });
  await page.waitForTimeout(4000);
  const el = await page.\$('.poster.xhs');
  await el.screenshot({ path: '/tmp/claire-ip-card/output.png', fullPage: false, type: 'png' });
  await browser.close();
  console.log('done');
})();
"
```

- Save rendered images in `output/`.
- Verify dimensions and inspect the rendered PNGs.

**Playwright viewport sizes:**
| Board | Width | Height |
|-------|-------|--------|
| `.poster.xhs` (3:4) | 1080 | 1440 |
| `.poster.square` (1:1) | 1080 | 1080 |
| `.poster.wide` (21:9) | 2100 | 900 |

**Do not use `image_generate` / fal.ai** for any output — always HTML + Playwright.

### 6. Image And Screenshot Handling

When the user provides screenshots:
- Preserve screenshot content unless the user asks for redesign.
- Prefer programmatic framing: target-ratio canvas, safe padding, clean background, readable screenshot.
- Do not stretch screenshots.

#### Text-On-Image Composition

Whenever a poster places text on top of a photo, follow `references/image-overlay.md`:
- **Selection first, tint only if needed.**
- **Subject mapping is mandatory.**
- **Crop discipline — set `object-position` inline on every photo.**
- **Thumbnail test.** Downscale the rendered PNG to 360 px wide and confirm the title is still legible.

Editorial dark covers and Swiss covers with hero photos both require these checks.

#### Web-Sourced Images (fallback when user has none)

When the user has no screenshots/photos and a generated bitmap would not fit the page's role, fetch from the web instead of leaving the page thin.

Policy: **grab first, disclose after, let the user decide on attribution.**

Recommended sources (all free-tier, in order):
1. **Unsplash** — outdoor / lifestyle / atmospheric backdrops
2. **Pexels** — supports Chinese keyword search natively, best for China-specific scenes
3. **Flickr CC-licensed pool** — documentary realness, people-in-context
4. **Wallhaven** — game / anime / wallpaper themes
5. **Direct web search** — specific subject needed

How to fetch: use WebFetch or `curl` to download the image into `assets/`. Name the file by purpose (e.g. `assets/hero-mountain.jpg`). Record source URL in `assets/SOURCES.md`.

After fetching, surface the provenance to the user **before** finalizing the design.

### 7. Deliver

**Show user first, validate on request.** Default flow:

1. After rendering completes, immediately show the user the rendered images inline with `MEDIA:path` format and a one-sentence summary.
2. Ask: **"先你自己看，还是我先自动核查一遍？"**
3. If user says "我自己看" / "no need" — stop here, let them inspect.
4. If user says "你查吧" / "auto-check" — only then run `node validate-social-deck.mjs <task-dir>`, fix any FAIL, and re-render.

Never silently run the validator before showing the user.

## 文章金句卡片模式（Pull Quote Card）— 2026-06-06 验证

当文章含有名人名言或核心观点句，适合生成"金句卡片"配合文章发布。

**适用场景：**
- 公众号文章内嵌配图（每张对应一个金句）
- 小红书长文配套（每张对应一个关键观点）
- 不是封面图，是章节/观点的视觉锚点

**版式规格：**
- 画布：1080×1440（3:4竖版）
- 风格：Editorial × Midnight Ink（深色底+金色accent）
- 内容：一句引用 + 作者来源 + 装饰线

**快速 HTML 模板（无需加载完整 seed）：**
```html
<!doctype html>
<html lang="zh-CN" data-theme="midnight-ink">
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
  <style>
    :root {
      --serif-zh: "Noto Serif SC", serif;
      --mono: "IBM Plex Mono", monospace;
    }
    [data-theme="midnight-ink"] {
      --paper:#0e0d0c; --paper-2:#1a1714; --ink:#ece2cf;
      --muted:#9a8c75; --line:rgba(236,226,207,.22);
      --accent:#d4a04a; --accent-soft:#3a2a14;
      --ink-rgb:236,226,207; --accent-rgb:212,160,74;
    }
    *,*::before,*::after{box-sizing:border-box;}
    body{margin:0;padding:0;background:#1a1a1a;
      display:flex;flex-direction:column;gap:40px;padding:48px 24px;
      align-items:center;}
    .card{
      width:1080px;height:1440px;background:var(--paper);
      color:var(--ink);position:relative;overflow:hidden;
      display:flex;flex-direction:column;justify-content:center;
      padding:96px 88px;isolation:isolate;
    }
    /* 必须的三层背景 */
    .grain{
      position:absolute;inset:0;z-index:1;pointer-events:none;
      opacity:.26;mix-blend-mode:screen;
      background-image:radial-gradient(rgba(255,244,214,.10) 1px,transparent 1px);
      background-size:3px 3px;
    }
    .paper-wash{
      position:absolute;inset:0;z-index:1;pointer-events:none;
      background:radial-gradient(80% 50% at 28% 16%, rgba(212,160,74,.12), transparent 64%),
                radial-gradient(70% 60% at 80% 86%, rgba(60,40,20,.20), transparent 72%),
                linear-gradient(180deg, rgba(236,226,207,.02), rgba(0,0,0,.32));
    }
    .kicker{font-family:var(--mono);font-size:20px;letter-spacing:.22em;
      text-transform:uppercase;color:rgba(var(--ink-rgb),.55);margin:0 0 20px;}
    .rule-accent{height:2px;background:var(--accent);border:0;margin:0 0 28px;width:80px;}
    .pullquote{font-family:var(--serif-zh);font-style:italic;font-weight:500;
      font-size:60px;line-height:1.28;color:var(--ink);margin:0 0 36px;}
    .source{font-family:var(--mono);font-size:19px;letter-spacing:.16em;
      text-transform:uppercase;color:var(--accent);margin:0;
      border-top:1px solid var(--line);padding-top:18px;width:100%;}
    .issue-strip{
      position:absolute;left:88px;right:88px;bottom:52px;
      display:flex;justify-content:space-between;align-items:center;
      font-family:var(--mono);font-size:17px;letter-spacing:.12em;
      text-transform:uppercase;color:var(--muted);
      border-top:1px solid var(--line);padding-top:16px;
    }
  </style>
</head>
<body>
<!-- 每张卡片一个 section，id 用于 Playwright 定位截图 -->
<section class="card" id="card-01">
  <div class="grain"></div>
  <div class="paper-wash"></div>
  <p class="kicker">Morgan Housel · 摩根·休斯</p>
  <div class="rule-accent"></div>
  <p class="pullquote">The highest form of wealth is the ability to wake up every morning and say, "I can do whatever I want today."</p>
  <p class="source">The Psychology of Money</p>
</section>
</body>
</html>
```

**渲染脚本：**
```bash
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file:///path/to/index.html', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  const ids = ['card-01','card-02'];
  for (let i = 0; i < ids.length; i++) {
    const el = await page.\$('#' + ids[i]);
    await el.screenshot({ path: '/tmp/output/card-0'+(i+1)+'.png', fullPage: false, type: 'png' });
  }
  await browser.close();
})();
"
```

**发送格式：** 每张图单独发飞书，用 `MEDIA:/path/to/card-0N.png`，不要合并成一张图发送。

**带品牌栏版本（2026-06-07验证）：** 在金句卡片底部追加96px 固定品牌 strip：
```html
<div class="brand-strip">
  <span class="account">公众号：不躺平的钱</span>
  <span class="name">Claire CHEN</span>
</div>
```
对应 CSS追加：
```css
.brand-strip {
  position: absolute; left: 0; right: 0; bottom: 0; height: 96px;
  background: rgba(212,160,74,.08);
  border-top: 1px solid rgba(212,160,74,.25);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 88px; z-index: 3;
}
.brand-strip .account {
  font-family: var(--sans-zh); font-size: 22px; font-weight: 500;
  color: var(--accent); letter-spacing: .12em;
}
.brand-strip .name {
  font-family: var(--serif-en); font-size: 22px; font-weight: 400;
  color: rgba(var(--ink-rgb), .65); letter-spacing: .18em;
}
```
流程：生成 HTML → Playwright screenshot → 发飞书蛮子确认 → 上传公众号素材库（add_material 接口）。

---

## Non-Negotiables

- **Never call `image_generate` or fal.ai.** Always HTML + Playwright.
- Never edit the original Guizang PPT skill or any upstream skill copied from elsewhere.
- Do not create random decorative SVG ovals, blobs, rain drops, stickers, or meaningless circles.
- Do not use nested cards or generic SaaS card layouts as the default.
- Do not let text overflow, touch the edge, or collide with the footer band.
- Do not let text become too small to read on mobile.
- Do not write inline `font-size` + `font-weight` on display titles in Swiss. Use the typed classes.
- Do not deliver Editorial posters with a flat paper background, mono labels on every row, and no atmosphere layer.
- Do not fake data, release details, or percentages.
- Do not crop faces, key UI text, or hardware/product details unless the user explicitly accepts it.
- Do not reuse a 21:9 cover by blindly cropping it into 1:1. Compose each ratio separately.
- **3:4 卡必须吃满画布** — content must cover ≥75% of canvas height. Any >15% pure-whitespace band needs a stated reason.
