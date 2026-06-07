# qifan 研学营文件对应关系

## PDF 信息
- 文件名: （7月7日发团）启富未来-深港科创亲子研学营4天3晚.pdf
- 实际路径: `/home/agentuser/.hermes/cache/documents/doc_ff9bdf78a595_（7月7日发团）启富未来-深港科创亲子研学营4天3晚.pdf`（23MB，共20页）
- ⚠️ `doc_bcf0d09c657a_` 路径不存在，不要使用

## 已提取图片（12张，resized_p5~p16.jpg）
- 目录: `/home/agentuser/.hermes/hermes-agent/web/public/qifan/`
- 这些图是从 PDF 正确渲染出来的，大小在 64-87KB 之间
- 当前放在 HTML 里"活动之后"的位置，需要排版调整

## 图片 → PDF 页码映射（严格）
| 图片 | PDF页 | 内容 |
|---|---|---|
| resized_p5.jpg | P5 | 学生 DAY1 上 |
| resized_p6.jpg | P6 | 学生 DAY1 下 |
| resized_p7.jpg | P7 | 学生 DAY2 上 |
| resized_p8.jpg | P8 | 学生 DAY2 下 |
| resized_p9.jpg | P9 | 学生 DAY3 上 |
| resized_p10.jpg | P10 | 学生 DAY3 下 |
| resized_p11.jpg | P11 | 学生 DAY4 |
| resized_p12.jpg | P12 | 家长 DAY1 上 |
| resized_p13.jpg | P13 | 家长 DAY1 下 |
| resized_p14.jpg | P14 | 家长 DAY2 |
| resized_p15.jpg | P15 | 家长 DAY3 |
| resized_p16.jpg | P16 | 家长 DAY4 |

## HTML 文件版本
- 当前运行版本: `启富未来-研学营-beta版本.html`
- 蛮子发来新文件: `启富未来-研学营-beta版本_2_.html`（路径: `/home/agentuser/.hermes/cache/documents/doc_f34ce55de05f_启富未来-研学营-beta版本(2).html`）
- 需要对比两个版本差异

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

## 已知问题（不要重复尝试）
Chromium HTTP 访问 PDF 会导致空白截图（下载保护）。不要用 `http://localhost:PORT/page_X.pdf` 方式。