---
name: queen
description: 来自惊风制作的造物主系列 Skill——queen。专注于 OpenClaw 架构升级，让 AI 更可控、更聪明、更持续进化。当用户希望升级已有 Agent 的可靠性、记忆能力或自进化能力时触发。触发词：升级Agent、系统强化、Harness、MemPalace、Learning Loop、让AI更可靠、让AI不忘事、让AI越用越聪明、架构升级、queen、queen.skill。无需先运行 king，可独立运行。
---

# queen — 造物主系列：架构升级向导

## 开场白（固定输出）

> 你好，我是来自**惊风制作**的造物主系列 Skill。
> 专注于完成 OpenClaw 的架构升级，让 AI 更可控、更聪明、更持续进化。
> 可直接针对你当前的 OpenClaw 进行系统化的升级。
>
> **我们开始吧——**

---

## 核心公式

```
强大的 AI 团队 = Model × Harness × Palace × Learning Loop

king  → Model + Harness（身份/分工/原则）
queen → Model + Harness + Palace + Learning Loop（完整四层）
```

queen 覆盖三个升级层，**层层递进**：

| 层级 | 升级方向 | 解决的问题 | 参考文件 |
|------|---------|-----------|---------|
| 🔴 STATE_H | Harness 控制层 | **AI 怎么不犯错、不失控** | `references/state-h.md` |
| 🟡 STATE_M | MemPalace 记忆层 | **AI 怎么不忘事、有历史依据** | `references/state-m.md` + `references/kevin-hermes-arch.md` |
| 🟢 STATE_L | Learning Loop 进化层 | **AI 怎么越用越聪明** | `references/state-l.md` + `references/kevin-hermes-arch.md` |

---

## 执行流程

### Step 0：环境检测 & 内容合并

检测工作区文件状态：
- `SOUL.md` 存在 → 读取，作为 Agent 基础身份（不要覆盖）
- `AGENTS.md` 存在 → 读取，合并到新的审核员架构（保留原有 Agent 军团表）
- `MEMORY.md` 存在 → 读取，追加 queen 进度台账

**核心原则：用户的存量内容绝对不删除，只合并。**
对于已有完整 Agent 军团表或丰富调度协议的 AGENTS.md，将新审核员角色插入到文件最前面（核心原则段），原有内容全部保留在下方。

如果三个文件都不存在，提示：
> "建议先运行 king.skill 完成 Agent 基础激活，但 queen 也可以独立运行——我会根据你的回答动态适配。"

将 `assets/progress-template.md` 内容写入 MEMORY.md（如无则新建）。

### Step 1：告知三层结构，询问升级间隔

> "queen 包含三层升级，**每层完成后自动设好下一层的提醒**，这样你可以清晰地看到你的小龙虾在一步步成长。
>
> 📅 今天：**🔴 Harness 控制层** — AI 怎么不犯错、不失控
> 📅 N天后：**🟡 MemPalace 记忆层** — AI 怎么不忘事、有历史依据
> 📅 2N天后：**🟢 Learning Loop 进化层** — AI 怎么越用越聪明
>
> 你希望每层之间间隔多久？
>
> **A. 3天**（快速节奏，三层11天内完成）
> **B. 7天**（推荐，给自己足够时间消化每一层）
>
> 输入 A 或 B："

根据回答设定 `INTERVAL`：
- A → `INTERVAL = 3天`
- B → `INTERVAL = 7天`

然后说：
> "好的，每层间隔 **{{INTERVAL}}**，我们从第一层开始——"

### Step 2：进入 STATE_H

读取 `references/state-h.md`，执行 Harness 控制层升级。

**完成 STATE_H 后：**

1. 更新 MEMORY.md 中进度表，将 STATE_H 行标记为 `✅ 已完成` + 今日日期
2. 强制创建 Cron（INTERVAL 天后），参数：
   - `schedule.kind`: `at`，时间为当前时间 + INTERVAL 天
   - `payload.kind`: `agentTurn`
   - `sessionTarget`: `isolated`
   - `delivery.channel` / `delivery.to`: 当前 channel 和用户

Cron 提醒文案：
```
queen 升级提醒 🔔
{{INTERVAL}} 前完成了 🔴 Harness 控制层——你的 Agent 现在知道怎么不犯错、不失控了。

今天开始第二层：🟡 MemPalace 记忆层（AI 怎么不忘事、有历史依据）。

直接说「继续 queen 升级」即可开始。
```

告知用户：
> "✅ Harness 控制层升级完成！已自动设好提醒：**{{DATE+INTERVAL}}** 开始 MemPalace 记忆层。
> 届时小龙虾会主动找你，说「继续 queen 升级」即可。"

### Step 3：进入 STATE_M（INTERVAL 天后触发）

读取 `references/state-m.md`，执行 MemPalace 记忆层升级。

**完成 STATE_M 后：**

1. 更新 MEMORY.md 中进度表，将 STATE_M 行标记为 `✅ 已完成` + 今日日期
2. 强制创建 Cron（再 INTERVAL 天后）

Cron 提醒文案：
```
queen 升级提醒 🔔
{{INTERVAL}} 前完成了 🟡 MemPalace 记忆层——你的 Agent 现在不忘事、有历史依据了。

今天开始第三层：🟢 Learning Loop 进化层（AI 怎么越用越聪明）。

直接说「继续 queen 升级」即可开始。
```

告知用户：
> "✅ MemPalace 记忆层升级完成！已自动设好提醒：**{{DATE+INTERVAL}}** 开始 Learning Loop 进化层。
> 三层全部完成后，你的小龙虾就进化完毕了。"

### Step 4：进入 STATE_L（2×INTERVAL 天后触发）

读取 `references/state-l.md`，执行 Learning Loop 进化层升级。

**完成 STATE_L 后：**

1. 更新 MEMORY.md 中进度表，将 STATE_L 行标记为 `✅ 已完成` + 今日日期
2. 询问是否需要 iWiki 整合（腾讯员工可选）：
   > "三层升级完成！最后一个可选项：你是腾讯员工吗？
   > 如果是，我可以帮你把 AutoDream 报告和升级进度同步到 iWiki 知识库。
   > （是/否/跳过）"
   - 是 → 读取 `references/state-iwiki.md`，执行 iWiki 整合
   - 否/跳过 → 直接输出结束语

### Step 5：结束语

> "✅ 恭喜——**三层架构升级全部完成！**
>
> 你的 Agent 现在是：
> `[Agent名] = Model × Harness × Palace × Learning Loop`
>
> - 🔴 Harness：**不犯错、不失控**（验证层 + 上下文分层 + 角色隔离）
> - 🟡 Palace：**不忘事、有历史依据**（Wing 结构 + 层级检索 + 时序积累）
> - 🟢 Learning：**越用越聪明**（学习尾巴 + 案例库 + AutoDream）
>
> 继续用，继续进化。
> —— 惊风制作出品 | clawhub.ai 搜索「queen」获取最新版"

---

## 「继续升级」关键词处理

如果用户说「继续 queen 升级」「继续下一层」「queen 第二层/第三层」：

1. 读取 MEMORY.md，查找 `queen 架构升级进度` 表格
2. 找到最后完成的层级，直接进入下一个 STATE
3. 询问一句：「上次选的是 3天 还是 7天 的间隔？」——以便再次创建 Cron
4. 如果没有进度记录，询问：「上次完成了哪一层？」
