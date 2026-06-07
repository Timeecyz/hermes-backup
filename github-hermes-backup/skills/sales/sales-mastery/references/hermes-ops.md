# Hermes 个人部署运维手册

> 蛮子专属 Hermes 环境运维指南。记录了自己的基础设施在哪里、怎么维护、出了问题怎么找。

---

## 核心架构

```
GitHub Backup (Timeecyz/hermes-backup)
    ↓ 每天03:00自动推送
~/.hermes/                          # 主目录
├── skills/                         # 97个skills全量
├── memories/
│   ├── MEMORY.md                  # 长期记忆（蛮子偏好/工作方式/subagent状态）
│   └── USER.md                     # 用户画像
├── cron/
│   ├── jobs.json                  # 所有定时任务
│   └── scripts/
│       └── hermes_backup.sh       # 备份脚本（全量skills）
├── SOUL.md / AGENTS.md / MEMORY.md # 核心配置
├── config.yaml                     # Hermes配置
└── sessions/                       # 对话记录SQLite

本地 Subagent Workspaces:
~/.openclaw/workspace/
├── health-expert/    (SOUL.md + AGENTS.md)
├── investment-expert/ (SOUL.md + AGENTS.md)
└── sales-coach/       (SOUL.md + AGENTS.md + SKILL.md)
```

---

## 日常运维命令

### Gateway 状态检查
```bash
hermes gateway status
journalctl -n 50 --no-pager | grep -i gateway  # 重启/崩溃日志
tail -100 ~/.hermes/logs/gateway.log           # 实时日志
```

### 手动备份（立即执行）
```bash
cd ~/.hermes/cron/scripts && bash hermes_backup.sh
# 或手动触发
cd /tmp/hermes-backup-repo && git pull origin master && git log --oneline -3
```

### 查看定时任务
```bash
hermes cron list
```

### 查看 skills 列表
```bash
hermes skills list
```

---

## 访问方式

### TUI 界面（终端全屏）
```bash
hermes --tui
```
在另一个终端窗口运行，与飞书对话窗口并存。

### Web API Server（未启用）
端口 8642，当前未监听。如果需要浏览器面板访问，需配置 `platforms.api_server` 并重启 gateway。

### 飞书（当前主要通道）
当前通过飞书 IM 平台正常接入，无需额外配置。

---

## 备份策略（已修复 2026-06-05）

**旧策略（失效）：** 只备份 `skills/SKILL.md` + 部分指定目录  
**当前策略：** 全量 `skills/` 目录 + `memories/` + 核心配置

脚本位置：`~/.hermes/cron/scripts/hermes_backup.sh`

备份内容：
- `MEMORY.md`, `SOUL.md`, `AGENTS.md`
- `memories/USER.md`, `memories/MEMORY.md`
- `config.yaml`, `cron/jobs.json`
- `skills/` （全量90+个skills）

---

## GitHub 备份仓库

| 仓库 | 内容 | 频率 |
|------|------|------|
| `Timeecyz/hermes-backup` | 全量备份tar.gz + memories | 每天03:00 |
| `Timeecyz/-openclaw-workspace` | openclaw workspace（含skills/subagents/脚本） | 手动 |

**手动推送到GitHub：**
```bash
cd /tmp/hermes-backup-repo
git add -A
git commit -m "描述"
GIT_TERMINAL_PROMPT=0 git push origin master
```

⚠️ **注意：** GitHub Push Protection 会拦截 MEMORY.md 中的明文 Token。Token 已脱敏处理，push 前确认内容不含明文。

---

## Subagent 部署流程（2026-06-05已部署）

当需要从 GitHub 备份恢复或部署新 subagent 时：

```bash
# 1. 克隆备份仓库
cd /tmp && git clone https://github.com/Timeecyz/-openclaw-workspace.git

# 2. 找到对应 subagent 文件
ls -la -openclaw-workspace/subagents/

# 3. 创建 workspace 目录
mkdir -p ~/.openclaw/workspace/<agent-name>/

# 4. 复制文件
cp subagents/<agent-name>/SOUL.md \
   subagents/<agent-name>/AGENTS.md \
   subagents/<agent-name>/SKILL.md \
   ~/.openclaw/workspace/<agent-name>/

# 5. 测试：用 delegate_task 调用
```

已部署的 subagent：
- `health-expert/` — 健康管理专家
- `investment-expert/` — 投资专家
- `sales-coach/` — 销售教练

---

## 已知限制

1. **API Server 未启用** — 浏览器面板端口 8642 未监听，TUI 是当前可用的图形化方式
2. **gh CLI 未安装** — GitHub 操作使用 `curl + git` 直接操作
3. **subagent 无独立路由** —昊总 DM 尚未接入学习助手模式（待实现）

---

## 故障排查

| 症状 | 检查命令 | 可能原因 |
|------|---------|---------|
| Gateway 无响应 | `journalctl -n 50 \| grep gateway` | SIGTERM重启/崩溃 |
| 备份失败 | `bash hermes_backup.sh` 手动跑 | 网络/权限/Token过期 |
| 定时任务未执行 | `hermes cron list` 看last_status | cron配置问题 |
| 推送被GitHub拦截 | 检查MEMORY.md是否有明文Token | Push Protection |

---

*最后更新：2026-06-05*