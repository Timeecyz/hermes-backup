# Production Workflow

## Recommended Folder Shape

Create a task folder under the current workspace:

```text
social-card-<slug>/
  index.html
  render.cjs
  assets/
  output/
```

Use descriptive slugs:

- `social-card-doubao-input`
- `social-card-hiking-outfit`
- `wechat-ai-card-skill-cover`

## HTML/CSS Rendering Pattern

Build one HTML file containing all frames:

```html
<main class="sheet">
  <section class="poster xhs" id="xhs-01">...</section>
  <section class="poster xhs" id="xhs-02">...</section>
  <section class="cover wechat wide" id="wechat-21x9">...</section>
  <section class="cover wechat square" id="wechat-1x1">...</section>
  <section class="wechat-pair-preview" id="wechat-pair-preview">
    <div class="preview-wide">...</div>
    <div class="preview-square">...</div>
  </section>
</main>
```

Each frame must have stable dimensions:

```css
.xhs {
  width: 1080px;
  height: 1440px;
}

.wechat.wide {
  width: 2100px;
  height: 900px;
}

.wechat.square {
  width: 1080px;
  height: 1080px;
}

.wechat-pair-preview {
  width: 2400px;
  min-height: 1180px;
}
```

Use `box-sizing:border-box`, fixed safe margins, and `overflow:hidden`.

For WeChat covers:

- Compose `wechat-21x9` and `wechat-1x1` as separate source frames.
- Also include `wechat-pair-preview` in the same HTML so the pair can be inspected together.
- Export the two real deliverables separately.
- Export the pair preview only when helpful for review.
- The `1:1` cover should use a simplified title derived from the long title, not a crop or text squeeze from the `21:9` frame.

For electronic-magazine pages, place background canvases inside each `.poster` instead of relying only on CSS color:

```html
<section class="poster magazine hero" id="xhs-01">
  <canvas class="mag-bg" data-bg="ink-flow"></canvas>
  <div class="grain"></div>
  <div class="content">...</div>
</section>
```

The skill includes a reusable helper at `assets/magazine-bg-webgl.js`. Copy or inline it into the generated project when a WebGL background is useful.

## Rendering

**Recommended command — npx playwright screenshot (always works):**

```bash
npx playwright@latest screenshot --browser chromium --full-page \
  "file:///<absolute-path>/index.html" "/output/card-N.png" \
  --wait-for-timeout=4000
```

For single-card targeting by id:
```bash
npx playwright@latest screenshot --browser chromium --full-page \
  "file:///.../index.html#card-id" "/output/card-id.png" \
  --wait-for-timeout=4000
```

**WebGL background wait:** If using `magazine-bg-webgl.js` (ink-flow canvas), wait ≥3500ms so the canvas fully renders before screenshot.

**⚠️ fal.ai permanently retired for蛮子 (2026-06-05):** Never use `image_generate` (fal.ai) for social cards or article covers. Always use guizang HTML+playwright. 豆包/即梦 prompts are for user-side generation only.

**⚠️ Local playwright require fails ("MODULE_NOT_FOUND"):** Do NOT try to fix the require path. Use `npx playwright@latest screenshot` — it bootstraps itself and is more reliable than any local install workaround.

**Rendering checklist:**
- [ ] Wait ≥3500ms if using ink-flow WebGL background
- [ ] Use `--full-page` for complete 3:4 card capture (1080×1440)
- [ ] Verify output: `file output.png` confirms dimensions
- [ ] Send PNG directly to user — no intermediate files

If a local dev server is needed for assets or font loading, start it and tell the user the URL. If `file://` rendering works, no server is required.

## Verification Commands

Useful checks on macOS:

```bash
sips -g pixelWidth -g pixelHeight output/*.png
```

For visual inspection in Codex:

- Use image viewing tools for local PNGs.
- Show final PNGs inline with absolute paths.

## Screenshot Treatment

Programmatic framing is preferred for user-provided screenshots:

- Create a clean target-ratio frame.
- Add plain white, refined grey, or paper background. Do not add page-wide grid/dot backgrounds unless the user explicitly asks for a technical blueprint look.
- If the capture contains a floating window/card over unrelated UI, crop to the foreground subject before placing it.
- Place screenshot inside with safe padding.
- Preserve readable text.
- Do not redraw the screenshot unless the user asked for redesign.
- Do not add perspective, skew, rotation, or mockup tilt unless the user explicitly asks for a scene mockup.

For Swiss:

- Straight corners.
- No shadow by default.
- Hairline only if the screenshot edge disappears.

For editorial magazine:

- Small radius or subtle shadow is allowed, but avoid SaaS marketing-card styling.

## Generated Images

When generating missing visuals:

- Generate only the raw visual asset.
- Keep text out of generated images.
- Match the page role and style mode.
- Save generated assets into `assets/` and place them in the HTML.
- Generate only the pages that need it, usually 1-2 images for a set.

## Accessibility And Readability

- Use strong contrast for all text.
- Do not place long text over busy photos.
- If text must sit over photo, use a solid ink/paper block or a high-contrast strip, not a blur blob.
- Avoid negative letter spacing in Chinese body text.
- Use line-height that lets Chinese breathe: roughly 1.08-1.22 for big titles, 1.35-1.55 for body.

## Common Fixes

- Cover feels empty: enlarge title, enlarge image, or add a functional bottom strip.
- Screenshot too small: reduce side text, give screenshot 55%-70% of the canvas.
- Lower area empty: read `portrait-fill.md`; merge pages, add a full-height ledger, use a larger evidence image, add a marginal quote column, or switch to an atmospheric thesis page.
- Style feels generic: add issue metadata, better type hierarchy, a stronger evidence image, richer WebGL/ink atmosphere, or more intentional content dividers.
- Text overflows: shorten copy before shrinking type.
