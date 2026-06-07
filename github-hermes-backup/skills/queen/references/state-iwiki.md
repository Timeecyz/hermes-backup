# STATE_IWIKI：iWiki 整合层（腾讯员工可选）

> 触发条件：三层升级全部完成后，用户确认是腾讯员工
> 产出：AutoDream 报告同步 iWiki + 升级进度存档

---

## 做什么

两件事：

1. **在 iWiki 建立 queen 升级存档目录**（如果没有已有 iWiki 知识库，先引导建立）
2. **配置 AutoDream 报告自动同步到 iWiki**

---

## 执行步骤

### Step 1：检查 iWiki 知识库

读取 MEMORY.md，查找是否有 `iWiki 知识库` 段落（king STATE_T 产出）。

- **有**：直接用已有的主目录 docid，在其下创建 `TEAM-queen升级档案` 子页
- **没有**：
  > "你还没有 iWiki 知识库目录。需要先建一个吗？
  > （是 → 引导输入 iWiki spaceid 和主目录名 / 否 → 跳过 iWiki 整合）"

### Step 2：创建 queen 升级存档页

在 iWiki 主目录下创建子页 `TEAM-queen升级档案`，内容：

```markdown
# queen 升级存档

**升级完成时间**：{{DATE}}
**升级间隔**：{{INTERVAL}}

## 三层升级产出

### 🔴 Harness 控制层（{{STATE_H_DATE}}）
- 审核员角色：{{REVIEWER_NAME}}
- 上下文分层：已清理（{{LINE_BEFORE}} → {{LINE_AFTER}} 行）
- 成员上下文包：{{MEMBER_COUNT}} 个

### 🟡 MemPalace 记忆层（{{STATE_M_DATE}}）
- Wing 结构：{{WING_LIST}}
- 四层记忆架构：已配置
- Cron 改造：{{CRON_COUNT}} 个任务加入记忆加载/写入

### 🟢 Learning Loop 进化层（{{STATE_L_DATE}}）
- 学习尾巴：已加入 {{CRON_COUNT}} 个 Cron
- 案例库目录：{{CASE_WING}}
- Skill 版本台账：memory/skill-registry.md
- AutoDream Cron：每 {{AUTODREAM_PERIOD}} 触发一次

## AutoDream 历史报告
（AutoDream 运行后自动追加）
```

### Step 3：改造 AutoDream Cron，追加 iWiki 同步

在已创建的 AutoDream Cron Prompt 末尾追加：

```
【iWiki 同步 — AutoDream 报告后执行】
将本次 AutoDream 报告追加到 iWiki 文档（docid: {{IWIKI_QUEEN_DOCID}}）
格式：在「AutoDream 历史报告」章节末尾追加一个新的 H3 标题：
### AutoDream 报告 — {{DATE}}
[报告正文]
```

### Step 4：写回 MEMORY.md

在 MEMORY.md 追加：

```markdown
## queen iWiki 存档
- 升级档案：{{IWIKI_QUEEN_URL}}
- AutoDream 同步：已配置（每 {{AUTODREAM_PERIOD}} 自动追加）
```

---

## 完成提示

> "✅ iWiki 整合完成！
>
> - 升级存档已建立：{{IWIKI_QUEEN_URL}}
> - AutoDream 每次运行后会自动把报告写入 iWiki
>
> 你现在可以直接在 iWiki 查看 Agent 的成长轨迹了。"
