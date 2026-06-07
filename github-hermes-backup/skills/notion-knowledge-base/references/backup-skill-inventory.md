# Backup 技能清单 & 缺口记录

> 建立时间：2026-06-05
> 用途：追踪哪些 skills 被 hermes-backup.sh 备份，哪些漏掉了

---

## hermes-backup.sh 实际备份的 skills（硬编码列表）

以下 skills 在备份脚本的 tar 名单内，会被每日 03:00 备份：

```
hk-insurance-plan-parser/
insurance-analyzer/
insurance-policy-parser/
marketing-copy/
notion-knowledge-base/
sales-analyzer/
sales/client-file-management/
sales/insurance-sales-mastery/
sales/sales-deep-learning/
sales/sales-mastery/
sales-pipeline-tracker/
wechat-article-rewriting-clairestyle/
wechat-article-writing/
wechat-daily-report/
wechat-hot-topic-radar/
wechat-moments-viral-generator/
wechat-publisher/
wechat-topic-radar/
微信读书/
```

共 **17 个**，全部是保险/销售/微信运营相关。

---

## 本地存在但未加入备份的 skills（缺口）

以下 skills 在本地 `~/.hermes/skills/` 存在，但不在备份脚本名单内：
**如果需要备份，需要手动加入 hermes_backup.sh 的 tar 名单**

| Skill | 备注 |
|-------|------|
| `haozong-learning-assistant` | 昊总学习助手，重要 |
| `ian-xiaohei-illustrations` | 小黑怪诞风格配图，重要 |
| `queen` | OpenClaw 架构升级，重要 |
| `ai-insurance-advisor` | 中国大陆保险AI助手 |
| `akshare` / `akshare-finance` | 财经数据接口 |
| `customer-insight` / `customer-maintenance` | 客户洞察/维系 |
| `wechat-article-rewriting-clairestyle` | ✅ 已在备份名单 |
| 其他 mlops/media/research 等 | Hermes 内置技能，可选 |

---

## 更新方法

若要新增备份某 skill，编辑 `~/.hermes/cron/scripts/hermes_backup.sh`，
在 `tar -czf` 行加入 `skills/SKILL.md` 同级目录名。

**原则：只备份蛮子自定义的 skill，不备份 Hermes 内置技能。**