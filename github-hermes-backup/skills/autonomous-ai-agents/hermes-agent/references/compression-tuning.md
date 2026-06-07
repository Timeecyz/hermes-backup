# MiniMax M2.7 模型参数 & 上下文压缩调优

## 模型规格（MiniMax-M2.7）

| 参数 | 值 | 说明 |
|---|---|---|
| context_length | 204,800 tokens | 上下文窗口上限 |
| max_tokens | 32,000 tokens | 单次最大输出 | |
| provider | custom:minimax_coding | API base: https://api.minimaxi.com/anthropic |

> 数据来源：OpenRouter 模型目录（https://openrouter.ai/minimax/minimax-m2.7）、MiniMax 社区实测

## 压缩配置项（推荐值）

```yaml
compression:
  enabled: true
  threshold: 0.75          # 75%满了才压缩（原0.50太早）
  target_ratio: 0.25        # 压缩后保留25%（原0.20丢失太多）
  protect_last_n: 30        # 保留最近30条不压缩（原20太少）
  hygiene_hard_message_limit: 400
  protect_first_n: 3
```

### 每项改动的作用

- **threshold: 0.75** — 低于0.75不压缩。0.5意味着上下文刚到一半就开始压缩，内容没充分利用就被压缩了。调到0.75能让模型充分利用上下文再压缩。
- **target_ratio: 0.25** — 压缩后目标保留25%的历史上下文。0.2太低，每次压缩丢失太多对话历史；0.25是更合理的平衡点。
- **protect_last_n: 30** — 最近30条消息任何情况下都不压缩。20条太少，有些长对话最近的几轮关键内容会被意外压缩。调到30更稳妥。

## 需要重启网关

配置修改后必须 `/restart` 才能生效，修改配置本身不需要重启但网关读取配置是在启动时。

## model.context_length 和 max_tokens

- **context_length** — 告知 Hermes 上下文窗口上限，防止越界请求。
- **max_tokens** — 限制单次输出上限，不设的话可能输出到一半被截断。M2.7实测最大支持 32K，调低到 32K 是合理的安全值。