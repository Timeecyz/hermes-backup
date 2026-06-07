---
name: guizang-ppt-skill
description: 生成横向翻页网页 PPT（单 HTML 文件），含 WebGL 背景、章节幕封、数据大字报、图片网格等模板。提供两种风格：① "电子杂志 × 电子墨水"（衬线 + 流体背景 + 暖色） ② "瑞士国际主义"（无衬线 + 网格点阵 + IKB/柠檬黄/柠檬绿/安全橙高亮）。当用户需要制作分享 / 演讲 / 发布会风格的网页 PPT，或提到"杂志风 PPT"、"瑞士风 PPT"、"Swiss Style"、"horizontal swipe deck"时使用。
---

# Magazine Web PPT

> 来源：guizang-ppt-skill 由歸藏创建与维护，源仓库：https://github.com/op7418/guizang-ppt-skill

## 这个 Skill 做什么

生成**单文件 HTML** 的横向翻页 PPT，提供两种可选视觉基调：

### 风格 A · 电子杂志 × 电子墨水（默认）
- WebGL 流体/等高线/色散背景（hero 页可见）
- 衬线标题（Noto Serif SC + Playfair Display）+ 非衬线正文 + 等宽元数据
- 适合：人文分享、行业观察、商业发布、需要"杂志感"的演讲
- 美学锚点：像 *Monocle* 杂志贴上了代码

### 风格 B · 瑞士国际主义（Swiss Style）
- WebGL 极细网格 + 点阵背景（信息驱动设计）
- 全程无衬线（Inter + Helvetica + Noto Sans SC）+ 极致字号对比
- 高反差功能色：克莱因蓝 IKB / 柠檬黄 / 柠檬绿 / 安全橙（四选一）
- 适合：科技产品、数据汇报、设计/工程领域分享、年度总结
- 美学锚点：Massimo Vignelli + Helvetica Forever

**两种风格共享**：横向翻页（键盘 ← →、滚轮、触屏、ESC 索引）、Lucide 图标、Motion One 入场动效。

## 何时使用

**合适的场景**：线下分享 / 行业内部讲话 / 私享会 / AI 产品发布 / demo day / 带有强烈个人风格的演讲

**不合适的场景**：大段表格数据、图表叠加 / 培训课件 / 需要多人协作编辑

## 工作流

### Step 1 · 需求澄清（动手前必做）

7问澄清清单：

| # | 问题 | 为什么要问 |
|---|------|-----------|
| 1 | **风格 A 还是 B?**（电子杂志风/瑞士国际主义风） | 必须先问，决定用哪个 template + layouts + themes |
| 2 | **受众是谁？分享场景？** | 决定语言风格和深度 |
| 3 | **分享时长？** | 15分钟≈10页，30分钟≈20页 |
| 4 | **有没有原始素材？** | 有素材就基于素材，没有就帮他搭 |
| 5 | **有没有图片或截图？希望怎么处理？** | 决定图文版式、图片槽位 |
| 6 | **想要哪套主题色？** | 杂志风5套/themes.md / 瑞士风4套/themes-swiss.md |
| 7 | **有没有硬约束？**（必须包含XX数据/不能出现YY） | 避免返工 |

### Step 2 · 选模板和主题色

- 风格 A → `assets/template.html` + `references/themes.md`
- 风格 B → `assets/template-swiss.html` + `references/themes-swiss.md`

主题色只能从预设选，不能自定义。

### Step 3 · 填充内容

**重要预检**：写 slide 前先读模板的 `<style>` 块，确认类名存在。layouts 骨架使用的类名如果模板里没有，会 fallback 到默认样式——大标题字体错、卡片糊成一团。

布局选择：
- 风格 A → `references/layouts.md`（10种）
- 风格 B → 先读 `references/swiss-layout-lock.md`，再读 `references/layouts-swiss.md`（22种 S01-S22）

### Step 4 · 对照检查清单自检

生成后必须打开网页逐页看，不能只靠代码。必查项：
- 风格 A：大标题衬线 / 图片只用 height:Nvh / 图片不能贴底 / 中文标题≤5字
- 风格 B：全称无衬线 / 只有一个accent色 / 无渐变阴影圆角 / 极致字号对比

### Step 5 · 本地预览

直接浏览器打开 `index.html`。

### Step 6 · 迭代

90%的调整都是改 inline style（字号/高度/间距）。

---

## 资源文件结构

```
guizang-ppt-skill/
├── SKILL.md                  ← 你正在读
├── assets/
│   ├── template.html          ← 风格 A 种子
│   ├── template-swiss.html    ← 风格 B 种子
│   ├── screenshot-backgrounds/
│   └── motion.min.js
├── scripts/
│   └── validate-swiss-deck.mjs
└── references/
    ├── components.md
    ├── layouts.md
    ├── swiss-layout-lock.md
    ├── layouts-swiss.md
    ├── swiss-map-component.md
    ├── themes.md
    ├── themes-swiss.md
    ├── image-prompts.md
    ├── screenshot-framing.md
    └── checklist.md
```

> ⚠️ 网络原因，references/ 和 assets/ 尚未完整拉取。如需完整文件，执行：
> `cd ~/.hermes/skills/guizang-ppt-skill && git pull origin main`
> 或访问 https://github.com/op7418/guizang-ppt-skill 查看完整内容。

---

## 核心设计原则

### 风格 A
1. 克制优于炫技
2. 结构优于装饰
3. 内容层级由字号和字体共同定义
4. 图片是第一公民（只裁底部，保证顶部完整）
5. 节奏靠 hero 页交替

### 风格 B
1. 单一锚点色（一份deck只有一个accent）
2. 极致字号对比（主标题与正文比例≥8:1）
3. 无衬线只此一家
4. 直角纯色（不允许渐变/阴影/圆角）
5. 网格至上
6. Hairline是手术刀（1px极细分割线）