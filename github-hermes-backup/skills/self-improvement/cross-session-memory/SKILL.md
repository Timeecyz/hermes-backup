---
name: cross-session-memory
description: 跨会话记忆接续方案——让Hermes新会话自动续接上次的pending任务和上下文
triggers:
  - 新会话启动
  - 跨天继续工作
  - 长项目推进
---

# 跨会话记忆接续方案

## 核心问题
Hermes 每个 session 独立，新开对话或重启后 AI 完全不记得之前聊到哪、做到哪。

## 解决方案：两个机制

### 机制一：SOUL.md 启动指引
每次新会话开始时，自动执行：
1. 调 memory 读取所有条目，确认是否有未完成任务标记（pending）
2. 若有 pending 任务，调 session_search 搜索最近 3 条会话获取上下文
3. 扫描 ~/Documents/AI_Automation/ 和 AI 总结目录下的当天文件，看是否有新内容

### 机制二：memory 状态指针
格式（收工时覆盖更新，不累加，永远只有这一行）：
```
last: YYYY-MM-DD | done: 今日完成 | pending: 待办/悬案 | paths: 相关文件路径
```

作用：新 session 读到状态指针 → 知道时间线 + 进度 + 待续内容 → 调 session_search 补上下文。

## 来源
学习君文章（微信公众号：学贯西东）《AI助手总失忆？Hermes跨会话无缝接续方案》

## 适用场景
- 半夜排查 bug 查到一半，第二天早上继续
- 长项目跨多天推进
- 任何需要"昨天聊到哪，今天从哪继续"的场景

## 已知教训（Signal Log）

**Signal 3: 重复cron冗余 (2026-06-03)**
每日多次进度检查cron（14:30/16:30/18:30）发送相同内容。前一轮已发完整报告，后续 cron 浪费上下文重建。
→ 修复：cron 执行前先 session_search(limit=1) 查最近一次 delivered 输出。若 < 3小时前且主题相同，跳过或发一行"无更新"。

**Signal 4: 技能名冲突 (2026-06-03)**
`skill_view(name='sales-mastery')` 失败："Ambiguous skill name — 2 skills match"。
- `~/.hermes/skills/sales-mastery/SKILL.md`
- `~/.hermes/skills/sales/sales-mastery/SKILL.md`
→ 使用全路径 `sales/sales-mastery` 消歧。报告给 curator 合并。

## 注意事项
- 状态指针收工时必须更新，否则启动指引失效
- 不要在 memory 里存详细过程，只存指针；详细上下文存在 session_search 里