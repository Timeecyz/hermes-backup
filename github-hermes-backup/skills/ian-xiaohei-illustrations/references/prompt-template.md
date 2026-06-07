# 单张生图提示词模板

## 标准提示词框架

```
16:9 landscape Chinese editorial illustration.
Pure white background, no texture, no gradient, no shadow.
Black hand-drawn ink style, thin lines, slight wobble, not mechanical.
Small black creature with white dot eyes (Xiaohei) as the main actor doing [CORE ACTION].
A few short Chinese handwritten annotations in red, orange, or blue (2-8 characters each, max 5-8 annotations).
Generous white space — main subject occupies ~40-60% of the frame.
One clear concept: [CORE CONCEPT].
No PPT, no infographic, no business illustration, no cute cartoon, no UI screenshot.
Caption/annotation style: [ANNOTATION TEXT].
```

## 小黑参与方式（按结构类型选择）

| 结构类型 | 小黑动作 | 常用批注色 |
|---------|---------|-----------|
| 断点/障碍 | 小黑卡在断点里/伸手够不到 | 红色 |
| 流程/路径 | 小黑牵着线/搬运素材 | 橙色 |
| 分拣/筛选 | 小黑变漏斗/分拣东西 | 橙色 |
| 承接/交接 | 小黑盖章/递东西 | 红色/橙色 |
| 状态/隐喻 | 小黑在状态中 | 蓝色 |
| 挖坑/预警 | 小黑举警告牌 | 红色 |
| 并行/一鱼多吃 | 小黑切鱼/分装 | 橙色 |

## 示例提示词

**断点示意**：
```
16:9 landscape Chinese editorial illustration. Pure white background.
Black hand-drawn ink style. Small black creature with white dot eyes (Xiaohei) stuck in a breakpoint gap, reaching both arms out desperately but nothing comes through.
Orange arrows showing input blocked at the top and nothing coming out at the bottom.
A few short Chinese annotations: "断点" in red, "进不去" in blue, "出不来" in blue.
Generous white space. No PPT. No labels like "流程图". Clean and absurd.
```

**一鱼多吃（分发）**：
```
16:9 landscape Chinese editorial illustration. Pure white background.
Black hand-drawn ink style. Xiaohei holding a giant fish, slicing it into multiple equal portions on a workbench.
Orange arrows leading from each portion to separate destinations labeled with different platform names in blue handwritten style.
Short annotation: "一鱼多吃" in red at top left.
Generous white space, main subject ~50% of frame. Clean absurd product-sketch aesthetic.
```

## 颜色规则（严格执行）
- 黑色：线稿、角色、主要文字
- 红色：重点批注、问题、结果（偶尔）
- 橙色：主路径、箭头、流向（主要）
- 蓝色：补充说明、AI 状态、系统提示（克制）

## 禁止在提示词里出现
- "PPT"
- "infographic"
- "商业插画"
- "可爱卡通"
- "系统架构图"
- "流程图"
- "课程课件"
- "workflow diagram"
- 任何左上角类型标题