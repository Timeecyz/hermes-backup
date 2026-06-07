# Kevin's Hermes 三层架构 — 参考文献

> 来源：KevinAIStack 微信公众号三篇文章
> 学习时间：2026-06-07

---

## 核心框架：Personal Agent Stack 三层

```
协作层（房间/角色/发言权/看板/证据表/人工闸门）
执行层（Hermes/Claude Code/Codex/脚本/技能/Gateway）
情报层（Search/Fetch/浏览器/平台API/知识库）
```

来源：[Hermes Kanban/Agent Team 文章](https://mp.weixin.qq.com/s/lI4v-Jaf5sEKo9QOxTn4Yw)

---

## 各层详解

### 1. 记忆层 — Hindsight（对应 queen STATE_M）

**解决的问题：** Agent 记得去查，而非只记住。

**技术方案：** 知识图谱（不是纯向量检索）
- 8675 节点、672282 条链接、2600 条观察记录
- 三种记忆类型：经验、观察、世界知识
- 四种关系链：语义、时间、因果、实体
- 关键优势：「连带想起」——不是单条检索，是关系链推理

**配置教训（28 次变更踩坑）：**
- LLM 后端选型影响 retain 超时（轻量 Flash 模型稳定）
- 工具白名单冲突（后台 retain/recall 被安全策略拦截）
- 冷启动需种子导入（MEMORY.md 历史内容一次性灌入）
- 整合成本（每次整合调 LLM，API 成本累积）

**与 queen STATE_M 的关系：** Hindsight 是 MemPalace 记忆层的具体实现方案之一。

---

### 2. 情报层 — TinyFish + CloakBrowser（对应执行层）

**解决的问题：** Agent 现场看真实世界，而非只读 HTML。

**两段架构：**
- 第一段：Search/Fetch（找页面+抓内容）→ TinyFish
- 第二段：浏览器执行（看真实状态+保持登录态）→ CloakBrowser

**CloakBrowser 关键能力：**
- persistent profile（长期会话）
- 可见窗口 + CDP 连接（可人工接管）
- 登录/扫码/验证码交给人处理
- Agent 默认低频只读慢速操作
- 出异常/风控提示立即停下

**操作纪律：**
1. 优先连接已存在的浏览器会话，不每次重新启动
2. 使用独立 profile，不和普通浏览器混用
3. 登录/扫码/验证码全部交给人
4. Agent 默认低频、只读、慢速操作
5. 一旦出现验证/异常/风控提示，立即停下
6. 不把 CloakBrowser 宣传成"不会被检测"

---

### 3. 协作层 — Agent Team Runtime（对应 queen STATE_L）

**解决的问题：** 多 Agent 如何像一个小组一样工作，而非任务队列。

**五个核心能力：**
1. 共享上下文（不是各干各的）
2. 发言权调度（谁先说/后说/等/追问）
3. 角色边界（研究员/工程师/审稿人/协调者）
4. 可见的争论和验证（不要黑盒结果）
5. 人类闸门（权限/文件/外部发送必须介入）

**Hermes Kanban 定位：** 工作流内核，不是群聊协作。

**CUA 降级到边缘能力：**
能用 API 就用 API，能用结构化接口就用结构化接口，能让人确认就让人确认。CUA 只处理：没有 API、没有结构化接口、低风险、可回滚、可人工盯住的动作。

---

## Kevin 的 CUA 观点（重要修正）

> "我现在对 CUA 的期待降低了很多。不是说他没价值，而是把 CUA 当成 Agent Team 的核心能力，很容易走偏。"

**真实 CUA 问题：** 它不知道什么时候不该点，经常缺少稳定反馈，页面一变就可能失效，权限和风控成本很高，接入真实渠道出错影响被放大。

**结论：**真正的 Agent Team 应该先解决沟通、状态、权限和证据，操作界面只是最后一层。

---

## 三篇文章原文链接

1. Hindsight 记忆系统：https://mp.weixin.qq.com/s/zNErYSG0jMvTD9yxFR4r0Q
2. CloakBrowser 执行层：https://mp.weixin.qq.com/s/IuclMvqbDuUZvL6Bu_ypCw
3. Agent Team 协作层：https://mp.weixin.qq.com/s/lI4v-Jaf5sEKo9QOxTn4Yw