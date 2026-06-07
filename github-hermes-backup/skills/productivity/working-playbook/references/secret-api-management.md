# Secret & API 凭证管理规范

> 来源：2026-06-03 蛮子对话 | 蛮子原则：「别总是问我，自己先查」

---

## 凭证存储位置

**文件**：`~/.hermes/secret&API.md`

所有 API/Secret 凭证统一存在这里，不再分散。

---

## 新增凭证时

1. **先搜**：读 `secret&API.md`，搜索是否已存在
2. **再问**：确实没有才问蛮子
3. **存入格式**：

```markdown
## 服务名

**用途说明**
```
token/skey/secret
```

---

## 凭证文件结构模板

```markdown
## 服务名

**用途**
```
凭证内容
```
```

---

## 已确认存储的服务

| 服务 | 字段 | 蛮子是否知情 |
|------|------|------------|
| Notion | Integration Token + DB IDs | ✅ 已知 |
| 微信公众号 | AppID + AppSecret | ✅ 已知 |
| GitHub | PAT | ✅ 已知 |
| 飞书 | App ID + App Secret | ✅ 已知 |
| 微信读书 | API Key | ✅ 已知 |
| fal.ai | API Key (user:key格式) | ✅ 已知 |

---

## 蛮子说过的话

> 「你先查我的API，别总是问我」

> 「给我存到那个API.md里面」

**行动**：自己先搜、找不到再问蛮子，不要动不动就让蛮子重复。