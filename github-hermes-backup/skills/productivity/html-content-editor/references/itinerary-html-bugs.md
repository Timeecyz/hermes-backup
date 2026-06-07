# HTML 研学营页面 — 结构 Bug 与内容差异记录

> 来源：启富未来-深港科创亲子研学营 beta HTML vs 官方行程说明 docx
> 整理时间：2026-05-26

---

## 一、已发现的 HTML 结构 Bug

### Bug 1：住宿信息条（hotel-bar）格式崩溃 🔴

**位置：** HTML 第 206–214 行

**问题：** 多余 `</span>` 标签、酒店名称格式混乱

**原始代码（有bug）：**
```html
<div class="hotel-bar">
  <span><i class="fas fa-hotel"></i> 深圳4钻 + 香港4钻（2晚）</span>
  <span>参考酒店：   深圳酒店（四星）
德金花园、建国璞隐、中濠悦际、启悦嘉际
</span>
香港酒店（四星）
荃湾丝丽、荃湾悦品、悦品海景、悦来、华丽海湾、沙田丽豪</span>
  <span><i class="fas fa-utensils"></i> 地道港式围餐</span>
</div>
```

**修复后（参考）：**
```html
<div class="hotel-bar">
  <span><i class="fas fa-hotel"></i> 深圳4钻 + 香港4钻（2晚）</span>
  <span><i class="fas fa-bed"></i> 深圳：德金花园/建国璞隐/中濠悦际/启悦嘉际</span>
  <span><i class="fas fa-bed"></i> 香港：荃湾丝丽/悦品海景/悦来/华丽海湾</span>
  <span><i class="fas fa-utensils"></i> 地道港式围餐</span>
</div>
```

---

### Bug 2：家长行程缺少 card 包装容器 🔴

**位置：** HTML 第 348 行附近

**问题：** 家长行程区块直接以 `<div class="card" style="border-top: 4px solid #27ae60; margin-top: 0;">` 开始，缺少独立的 `card` 容器包裹整个家长 section

**修复：** 家长行程需要完整的 `.card` 包装，加上蓝色边框顶边，以及 `section-title` 标题行：

```html
<!-- 家长行程完整包装示例 -->
<div class="card" style="border-top: 4px solid #27ae60;">
  <div class="section-title" style="color:#27ae60;">
    <i class="fas fa-user-tie"></i> 家长行程
  </div>

  <!-- DAY 1 -->
  <div class="day-section">
    <div class="day-header">
      <span class="day-badge badge-d1">DAY 1</span>
      <span class="day-theme">科创启航 · 深圳</span>
    </div>
    <!-- 时间轴内容 -->
  </div>
</div>
```

---

### Bug 3：家长 Day 1 缺少 section-title  🟡

**位置：** 第 350 行附近

**问题：** 家长行程没有 `<div class="section-title">` 标题行，直接从 `day-header` 开始

---

### Bug 4：学生 Day 1 之前缺少分隔线 🟢

**问题：** 其他 Day 之间有 `<div class="divider"></div>`，但 Day 1 学生行程开头（hero 之后）没有

---

## 二、docx vs HTML 行程内容差异（重建时需同步）

### 学生行程对比

| 天 | docx 行程 | HTML 现状 | 差异 |
|----|-----------|---------|------|
| DAY 1 | 抵深集合 → 百度科技（无人驾驶/官方证书）→ 开营仪式 | 基本一致，但缺少「百度官方证书」强调 | 🟡 |
| DAY 2 | 香港科学馆（数理启蒙）→ 金管局（财商教育）→ 太平山顶 | 科学馆提前到 DAY2；无金管局财商描述 | 🔴 |
| DAY 3 | 港科大（学霸分享/名校课程/研学证书）→ 廉政公署（法治教育）→ 维港夜游 | 港科大在 DAY3 一致；无廉政公署；维港夜景在 DAY3 | 🔴 |
| DAY 4 | 数码港（AI赛车竞技）→ 结营颁奖 → 返程 | 数码港在 DAY4 ✓；无 AI 赛车强调 | 🔴 |

### 家长行程对比

| 天 | docx 行程 | HTML 现状 | 差异 |
|----|-----------|---------|------|
| DAY 1 | 抵深集合 → 百度科技 → 欢乐海岸/南头古城 | 基本一致 | 🟡 |
| DAY 2 | 海外资产配置私享会 → 金管局 → **香港赛马会** | 赛马会是新增亮点，HTML 完全没有 | 🔴 |
| DAY 3 | 港科大参访 → 自由购物 → 维多利亚港夜景 | HTML 有港科大但无赛马会；维港夜景在 DAY3 | 🟡 |
| DAY 4 | 自由购物 → 结营仪式 → 返程 | 基本一致 | 🟢 |

---

## 三、完整重建检查清单

当需要从 docx 重建整个行程 HTML 时：

- [ ] 住宿信息条 hotel-bar 格式正确（无多余 </span>）
- [ ] 学生行程 .card 有蓝色左边框顶边
- [ ] 家长行程有独立 .card 容器 + section-title + 绿色顶边
- [ ] 每个 DAY 之间有 .divider 分隔线
- [ ] 学生行程按 docx 最新内容同步
- [ ] 家长行程新增「香港赛马会」亮点
- [ ] 配图与行程内容匹配（等待用户提供素材）
- [ ] 底部 CTA / footer 信息完整
