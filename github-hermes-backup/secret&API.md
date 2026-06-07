# Secret & API 凭证汇总

> 找不到API就在这里先搜，搜不到再问蛮子。

---

## Notion

**Notion Integration Token**
```
[NOTION_TOKEN_REDACTED]
```
用途：读写Notion数据库和页面

**相关数据库ID（速查）**
| 用途 | Database ID |
|------|------------|
| 每日财经资讯存储 | 35ccd9aa-41cc-80f2-b550e111aeceb6bd |
| 读书+播客+课程学习笔记 | 349cd9aa-41cc-8017-a0f9-ff07a4a76b7d |
| 蛮子日记 / Quick Notes | 318cd9aa-41cc-80a2-a014-f82b2e49a671 |
| 蛮子方法库 | 372cd9aa-41cc-81cb-80c2-dd0d1c634bb7 |
| 「不躺平的钱」公众号内容库 | 34acd9aa-41cc-818f-aae0-c6ce9e77036f |

---

## 微信公众号

**AppID**
```
wx37f93a23f90770b4
```

**AppSecret**
```
c5fc89db461f4de7d55b65091979ce66
```

用途：
- 获取 access_token
- 推送草稿箱
- 上传素材（永久图片/缩略图用 `add_material`，临时用 `media/upload`）
- 查询草稿内容

**服务器IP（白名单用）**
```
111.229.192.217
```
如遇 40164 错误，需将此IP加入微信公众号后台 → 设置与开发 → 基本配置 → IP白名单

---

## GitHub

**Personal Access Token**
```
[GITHUB_PAT_REDACTED]
```

用途：操作仓库（commit、PR、issue等）

---

## 飞书（Lark/Feishu）

**App ID**
```
cli_aa9abc638cf91bb4
```

**App Secret**
```
2anV19EgpXL3r14ITxgoug2yatBn2eut
```

用途：
- 获取飞书 tenant_access_token
- 发送消息给蛮子（user_id: ou_72dbf7598ab4270ed7f5180bf41fd689）
- 读写飞书文档

**相关资源**
| 用途 | 链接/ID |
|------|---------|
| 启富未来CRM（飞书表格） | https://liuyufamilyoffice.feishu.cn/base/WXghb4GgCa1NO1sydjIcNCpZn2g |

---

## 微信读书

**API Key**
```
wrk-Xe508qCLT1mmtNkaRefYmgAA
```
用途：读取书架、笔记划线、书评等（需用户身份）

**获取方式**：微信读书App → 我 → 设置 → 体验增强 → 开启API权限 → 复制Key

**相关数据库ID（速查）**
| 用途 | Database ID |
|------|------------|
| 读书+播客+课程学习笔记 | 349cd9aa-41cc-8017-a0f9-ff07a4a76b7d |

---

## fal.ai（AI图片生成）

**API Key**
```
b3cdc6f5-4451-4fce-ae77-de9405b0b344:253e6030633d7eac5ef311cc0a7476c9
```
用途：AI图片生成（Dreamina、即梦等）

---

## 其他

如有新增凭证，随时追加到本文件。
格式：服务名 + Token/Secret + 用途说明

---

## 开拍APP

**API Key**
```
1dd98a3ea7cd4d1dbf6afe0e8e52a8d7
```

**Secret Key**
```
ca676bb8e24749ca9f9e6ef04bd8beb9
```

**用途**：视频创作辅助（待补充）