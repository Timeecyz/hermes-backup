# Self-Improving Agent — 跨会话学习与错误修正

> 建立时间：2025-05-25
> 更新：2026-06-05（新增：subagent 部署状态 vs MEMORY 蓝图的区别）

---

## 核心机制

每次出现以下情况，立即记录：
- 用户纠正了你的工作方式、风格、格式
- 你踩了坑并自己摸索出解决方案
- 发现某个skill/step过时或缺失
- 发现 MEMORY/技能库和实际情况不一致

---

## 已记录的教训

### 1. Subagent 部署状态 ≠ MEMORY 蓝图（2026-06-05）

**发现场景**：蛮子问"旗下子agent情况"，我查 `~/.openclaw/workspace/` 发现目录都不存在，但 MEMORY.md 记了调度规则。

**根本原因**：MEMORY.md 的 subagent 调度规则是"计划中的蓝图"，不是"已部署的现状"。

**教训**：
- 查 subagent 状态 → 查实际目录，不要只看 MEMORY
- 如果目录不存在，说明没部署，不能凭 MEMORY 调度
- 新部署 subagent 后，同步更新 MEMORY 标注状态

**验证命令**：
```bash
ls ~/.openclaw/workspace/          # 看实际有哪些 workspace
ls ~/.openclaw/workspace/<name>/    # 看该 workspace 下有哪些文件
```

---

### 2. hermes-backup.sh 只备份了 17 个 skills（2026-06-05）

**发现场景**：对照 GitHub hermes-backup 仓库和本地 skills 目录。

**教训**：
- 本地 97 个 skills，备份脚本只 tar 了 17 个（保险/销售/微信相关）
- 蛮子自定义的重要 skills（haozong-learning-assistant、queen、ian-xiaohei-illustrations）不在备份名单
- 备份策略：只备份蛮子自定义的，不备份 Hermes 内置技能

**更新方法**：编辑 `~/.hermes/cron/scripts/hermes_backup.sh`，在 tar 名单加 `skills/<name>/`

---

### 3. Notion API block_id 必须是纯 UUID（2025-05-25，已记录）

URL 中的 Page ID 带连字符，API 参数需要纯 UUID（去连字符）。

---

### 4. 回复前必搜历史（2025-05-25）

每次回复前用 session_search 搜相关上下文（当前话题 + "蛮子"），避免重复问已经确认过的事。

---

### 5. 公众号改稿必须说明原因（2025-05-25）

帮蛮子改公众号文章时，必须说「为什么要这样改」，让她能学习判断逻辑，不只是直接用。

---

*最后更新：2026-06-05*