# OpenClaw → Hermes 迁移备忘录

## 背景

用户从 OpenClaw 迁移到 Hermes Agent 时，备份仓库为 private，需要通过 GitHub API 读取。

---

## 关键发现

### 仓库名称

| 预期（错误） | 实际（正确） |
|-------------|-------------|
| `Timeecyz/openclaw-backup` | `Timeecyz/-openclaw-workspace` |

OpenClaw 的备份仓库名字带连字符 `-`，且前缀是 `-openclaw-workspace` 而非 `openclaw-backup`。

### 认证方式

`gh` CLI 未安装，使用 curl 直接调用 GitHub REST API：

```bash
# 先查仓库列表（确认正确名称）
curl -s -H "Authorization: token {TOKEN}" \
  "https://api.github.com/user/repos?per_page=100" | grep '"name"'

# 读取文件（Base64 编码内容）
curl -s -H "Authorization: token {TOKEN}" \
  "https://api.github.com/repos/{owner}/{repo}/contents/{path}"
```

响应 JSON 中 `content` 字段是 base64 编码的，需要解码：
```python
content_b64 = data["content"].replace("\n", "")
missing = len(content_b64) % 4
if missing:
    content_b64 += "=" * (4 - missing)
decoded = base64.b64decode(content_b64).decode('utf-8')
```

### 迁移脚本路径

`hermes claw migrate` 调用的底层脚本位于：
```
~/.hermes/hermes-agent/optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py
```

**不是** `~/.hermes/skills/migration/openclaw-migration/`（那个路径不存在）。

---

## 备份内容结构（openclaw-workspace 仓库）

```
openclaw-workspace/
├── SOUL.md              # 核心价值观
├── AGENTS.md           # 团队架构
├── MEMORY.md           # 77KB超大，包含营销规则/客户分级/Notion库
├── USER.md             # 用户偏好
├── IDENTITY.md        # Agent身份描述
├── TOOLS.md           # 工具清单
├── HEARTBEAT.md       # 自动任务配置
├── _backup/
│   ├── cron_jobs.json  # 13个定时任务（完整JSON）
│   ├── AGENTS.md
│   ├── HEARTBEAT.md
│   ├── IDENTITY.md
│   ├── MEMORY.md
│   ├── SOUL.md
│   ├── TOOLS.md
│   ├── USER.md
│   └── memory/
│       ├── 2026-03-31.md ~ 2026-05-xx.md   # 每日记忆文件
│       └── .dreams/
│           ├── daily-ingestion.json
│           ├── events.jsonl
│           ├── phase-signals.json
│           ├── session-corpus/            # 每日session记录
│           └── short-term-recall.json
```

---

## 迁移注意事项

### MEMORY.md 合并策略

备份的 MEMORY.md 有 77KB，内容包括：
- 营销全流程规则（4大专业领域话术）
- 客户分级标准
- Notion 数据库 ID（Journal/Quick Notes/港险资料库等）
- 17项习惯打卡规则
- 子Agent调度规则（投资专家/健康管理专家/销售教练）
- 产品知识（太平喜裕/太保萤火等）
- 日记自动化调度

**不能直接覆盖**，需要与当前 Hermes MEMORY.md 合并，保留 queen STATE_H 写入的内容。

### Cron Jobs 迁移

`_backup/cron_jobs.json` 包含 13 个 job，导出格式与 Hermes cron 不兼容，需要：
1. 逐一解析每个 job 的 `name`、`schedule.expr`、`payload.message`
2. 用 `cronjob` tool 重建

### USER.md / IDENTITY.md / TOOLS.md

可直接参考，用来更新 Hermes 对应文件，无需覆盖。

---

## 迁移流程（推荐）

1. **先用 `hermes claw migrate --dry-run` 预览**可迁移内容
2. **读取 GitHub 备份**（用 curl + API）确认实际内容
3. **分批迁移**：MEMORY.md 合并 → Cron jobs → USER/IDENTITY/TOOLS 参考更新
4. **不要盲目覆盖** SOUL.md / AGENTS.md（当前 Hermes 版本已有 queen STATE_H 新增内容）

---

*最后更新：2025-05-25*