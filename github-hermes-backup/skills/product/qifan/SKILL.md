---
name: qifan
description: 启富未来研学营 HTML 手册生成 — PDF 图片提取 + HTML 排版
triggers: qifan/启富未来/研学营/启富未来-研学营
---

# qifan 研学营项目

Generate HTML brochure pages for qifan (启富未来) study tour events, rendered from PDF source materials.

## 图片映射规则（严格匹配，不接受模糊分配）

| 图片文件 | PDF页码 | 内容 |
|---|---|---|
| p5.jpg | P5 | 学生 DAY1 上 |
| p6.jpg | P6 | 学生 DAY1 下 |
| p7.jpg | P7 | 学生 DAY2 上 |
| p8.jpg | P8 | 学生 DAY2 下 |
| p9.jpg | P9 | 学生 DAY3 上 |
| p10.jpg | P10 | 学生 DAY3 下 |
| p11.jpg | P11 | 学生 DAY4 |
| p12.jpg | P12 | 家长 DAY1 上 |
| p13.jpg | P13 | 家长 DAY1 下 |
| p14.jpg | P14 | 家长 DAY2 |
| p15.jpg | P15 | 家长 DAY3 |
| p16.jpg | P16 | 家长 DAY4 |

## 已知项目路径

- PDF: `~/.hermes/cache/documents/doc_ff9bdf78a595_（7月7日发团）启富未来-深港科创亲子研学营4天3晚.pdf`（23MB，共20页；另一同名路径 doc_bcf0d09c657a_ 实际不存在，不要用）
- HTML 运行版本: `~/.hermes/hermes-agent/web/public/qifan/启富未来-研学营-beta版本.html`
- beta_2 版本: `启富未来-研学营-beta版本_2_.html`（蛮子发来的新文件，存于缓存目录）
- beta_1 版本（原始）: `启富未来-研学营-beta版本.html`
- 运行版本通过 `python3 -m http.server 7890` 在 `web/public/qifan` 目录启动访问
- **图片路径说明**：HTML 内引用 `/resized_p5.jpg`，相对于 web 根路径，本地 HTTP 服务正常；微信内嵌浏览器可能无法显示（已知限制）
- **微信兼容方案**：若需在微信分享，可将 HTML 发布到公开 URL，或生成 PDF 作为附件分发
- 图片目录: `~/.hermes/hermes-agent/web/public/qifan/resized_p5.jpg ~ resized_p16.jpg`
- 图片缓存（用户发送的截图）: `/home/agentuser/.hermes/image_cache/img_*.jpg`
- 预览服务: `python3 -m http.server 7890`（工作目录：`web/public/qifan`）

## PDF 图片提取方法

## 图片处理方法（✅ 经验证有效）

蛮子本地打开 PDF 截图 → 通过飞书对话发送 → Agent 用 sharp resize 处理

**Agent 处理命令**（工作目录：`hermes-agent`）：
```bash
node -e "
const sharp=require('sharp');
sharp('/home/agentuser/.hermes/image_cache/<IMG_FILE>')
  .resize(800,null,{fit:'inside',withoutEnlargement:true})
  .jpeg({quality:85,optimize:true}).toFile('web/public/qifan/resized_p<N>.jpg')
  .then(()=>sharp('web/public/qifan/resized_p<N>.jpg').metadata())
  .then(m=>console.log('pN ok:',m.width,'x',m.height))
  .catch(e=>console.log('err:',e.message));
"
```

**关键发现**：用户每次发送图片，文件名都是新生成的（如 `img_89cfbe6db29c.jpg`），不是固定的 reuse 路径。每次都要从 `image_cache` 目录找最新的文件。
- 蛮子说"截图给你了但是你读取不了"时：不是真的读取不了，而是需要用 sharp 直接处理 image_cache 里的文件，不需要 vision_analyze
- 图片尺寸参考：蛮子截图通常是 1320x729（学生行程）或 1320x741（家长行程），resize 后 800px 宽，质量 85

## 微信内嵌浏览器兼容性（已知限制）
- HTML 里的图片路径 `/resized_p5.jpg` 是相对于 web 根路径
- 本地 HTTP 服务（`python3 -m http.server 7890`）可正常显示
- 微信内嵌浏览器可能无法显示图片（已知限制）
- 解决方案：若需在微信分享，可将 HTML 发布到公开 URL，或生成 PDF 作为附件分发

## 已知问题（不要重复尝试）
Chromium HTTP 访问 PDF 会导致空白截图（下载保护）。不要用 `http://localhost:PORT/page_X.pdf` 方式。
| PyMuPDF (pymupdf) | 环境未安装，pip 安装超时 |
| pdfjs-dist + node-canvas | canvas 模块未安装 |
| Playwright 打开 file:// PDF | Chromium 触发 download，无法渲染 |
| Playwright data: URL PDF | `ERR_ABORTED` — 浏览器当作附件下载 |
| Playwright HTTP server + object embed | 仍是 download 行为 |
| sharp 单独使用 | sharp 可用，但不支持直接渲染 PDF |

### 🔧 环境可用工具

- **Node.js**：`playwright`, `sharp`, `pdfjs-dist` (legacy mjs), `pdf-lib`
- **Python**：标准库为主，第三方图像库需安装

## 已知项目路径

- PDF: `~/.hermes/cache/documents/doc_ff9bdf78a595_（7月7日发团）启富未来-深港科创亲子研学营4天3晚.pdf`
- beta_2 版本: `启富未来-研学营-beta版本_2_.html`（蛮子发来的新文件，存于缓存目录）
- beta_1 版本（原始）: `启富未来-研学营-beta版本.html`
- 图片目录: `~/.hermes/hermes-agent/web/public/qifan/resized_p5.jpg ~ resized_p16.jpg`
- 预览服务: `python3 -m http.server 7890`（蛮子自己输入 URL 预览）
- **图片路径说明**：HTML 内引用 `/resized_p5.jpg`，相对于 web 根路径，本地 HTTP 服务正常；微信内嵌浏览器可能无法显示（已知限制）
- **微信兼容方案**：若需在微信分享，可将 HTML 发布到公开 URL，或生成 PDF 作为附件分发

## 工作流：处理蛮子发来的 HTML 文件

蛮子发来新的 HTML 文件（`启富未来-研学营-beta版本_2_.html`）时：

1. **保存位置**：`~/.hermes/cache/documents/doc_<hash>_启富未来-研学营-beta版本_2_.html`
2. **不要重新生成** — 这是蛮子已经做好的版本，不要用 PDF 重新提取图片
3. **检查图片路径**：确认 HTML 内图片是 `/resized_p5.jpg` 等相对路径，还是 base64
4. **启动预览服务**：`python3 -m http.server 7891 --directory ~/.hermes/cache/documents`（如果蛮子想预览缓存目录的文件）
5. **通知蛮子预览地址**

### beta_2 版本说明
- 文件名：`启富未来-研学营-beta版本_2_.html`（蛮子本地修改后的版本）
- 缓存路径：`/home/agentuser/.hermes/cache/documents/doc_f34ce55de05f_启富未来-研学营-beta版本(2).html`
- 若蛮子更新了文件，重新发送给我，我再更新缓存版本

---

## 蛮子的质量要求

- 图片必须和 PDF 内容严格对应，不能随意分配
- HTML 排版要体现每天行程的清晰结构
- 家长版和学生版分开呈现

## 参考
- `references/qifan-file-mapping.md` — 详细文件对应关系
- `references/beta2-html-notes.md` — beta_2 版本特有备注（图片路径、修改历史等）