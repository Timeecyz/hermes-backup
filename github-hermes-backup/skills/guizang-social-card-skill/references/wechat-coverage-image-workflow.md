# 公众号配图 + 草稿推送实战流程

> 来源：2026-06-04 蛮子「买了保险能随时退？」文章处理全程记录

## 关键结论

**当蛮子说"配图用guizang-黑金风格直接配"时 → 直接生成图片，推飞书预览 → 等确认后推草稿箱。**

她已经确认了风格，不需要再问"用哪种风格"。但图片还是需要飞书发给她看（不是自动推草稿箱），等她确认OK再推进。

## 完整流程（本次验证可行）

### 阶段1：内容确认
1. 用户发公众号链接 → 抓取 → 结构拆解 → 提供角度选项
2. 蛮子选方向 → 写Claire风格初稿 → 飞书发给她确认
3. 蛮子确认文字OK后，进入配图阶段

### 阶段2：配图生成（当蛮子已确认风格时）
1. 用户说"配图用XX风格直接配" → 直接用guizang-social-card-skill生成
2. 生成完毕 → 飞书发截图给蛮子预览（不说"你自己看"）
3. 蛮子反馈OK → 切图推送草稿箱

### 阶段3：草稿推送
1. 上传封面图到微信公众号素材库（add_material 接口）获取 media_id
2. 写入草稿（urllib.request 方式，避免 requests 的 Unicode 转义问题）
3. 草稿推送成功后告知蛮子

## 验证过的工具链

| 步骤 | 工具 | 命令/备注 |
|------|------|---------|
| HTML 生成 | guizang-social-card-skill | Midnight Ink 风格，生成 21:9 + 1:1 + PART配图 |
| 批量截图 | Playwright (node) | `node -e "const {chromium}=require('playwright');..."` |
| 截图单张导出 | `page.setViewportSize()` + `goto('#id')` + `screenshot()` | 每个 section 用 `id` 作为锚点 |
| 推草稿 | Python urllib | `json.dumps(..., ensure_ascii=False).encode('utf-8')` |
| 飞书发图 | `send_message` + MEDIA:路径 | 直接发图片附件给蛮子 |

## 黑金风格（Midnight Ink）公众号配图结构（本次验证）

```
21:9 主封面 → 标题 + 数据大字（32%）
1:1 方封面 → 简化标题 + 居中大字
PART01 配图 → 退保价值数据表（4列）
片尾Banner → 两个自检问题卡片
```

## 坑/注意事项

- Playwright 截图用 `playwright screenshot` CLI 无 `--viewport` 参数，必须用 Node.js API
- Midnight Ink 风格必须加 `.grain` + `.paper-wash` 两层背景，否则深色卡片糊成一团
- 草稿推送前必须先上传封面图获取 `thumb_media_id`（用 add_material 接口，不能用 media/upload）
- 蛮子确认流程：图片发飞书 → 等她回复OK/要改 → 再推草稿箱（不是自动推）

## 相关 Skill
- `guizang-social-card-skill` — 生成配图（已更新 Midnight Ink 适用范围说明）
- `wechat-article-rewriting-clairestyle` — 推草稿箱（STEP 5）