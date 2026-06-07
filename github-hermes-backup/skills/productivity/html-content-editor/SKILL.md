---
name: html-content-editor
description: "Edit HTML documents: replace images (base64/URL), swap text sections, update templates. For Feishu/HTML flyers, promotional pages, and structured HTML documents."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [HTML, image-insertion, base64, feishu, template-editing]
    related_skills: [ocr-and-documents, powerpoint]
---

# HTML Content Editor

Edit structured HTML documents — replace images, update text sections, insert content blocks. For Feishu/Lark flyers, promotional pages, event itineraries, and HTML-based marketing materials.

## Overview

Common task pattern: user provides an HTML file and one or more images with a placement instruction like「替换到DAY 1位置」. The workflow is:

1. **Confirm** the image and target position with the user
2. **Compress** the image (especially large PNGs from phones)
3. **Find** the target `<img>` tag in the HTML
4. **Replace** the src while preserving alt and other attributes
5. **Save** and verify

## Step 1: Image Compression

**Use ffmpeg (always available) — NOT PIL (often missing in sandbox)**

```bash
ffmpeg -i input.png -vf "scale=1200:-1" -q:v 2 -update 1 -y output.jpg
```

**Optimal target sizes:**
- For HTML inline display: width 1200px → typically 200-500KB
- For high-quality cards: width 2000px → typically 500-800KB
- `-q:v 2` = near-lossless JPEG quality

**Why not PIL:** The hermes sandbox often lacks `PIL`/`Pillow` installed. `ffmpeg` is always present on the system (`/usr/bin/ffmpeg`). Do not attempt to `pip install Pillow` in the sandbox — use ffmpeg instead.

**Handling oversized images for vision API:**
If an image needs vision analysis and exceeds 20MB base64:
1. Compress with ffmpeg first to ~500KB
2. Save to `/tmp/`
3. Use `/tmp/compressed.jpg` as the image_url for vision_analyze

## Step 2: Find Target Image Tag

Use regex to find all `<img class="day-img">` or similar structured tags:

```python
import re

with open('document.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'<img class="day-img"[^>]+>'
matches = [(m.start(), m.group()) for m in re.finditer(pattern, content)]

for i, (pos, tag) in enumerate(matches):
    alt_m = re.search(r'alt="([^"]*)"', tag)
    src_m = re.search(r'src="([^"]+)"', tag)
    alt = alt_m.group(1) if alt_m else ''
    b64_len = len(src_m.group(1)) if src_m else 0
    size_kb = b64_len * 3 // 4 // 1024
    print(f"[{i}] alt={alt} | {size_kb}KB | pos={pos}")
```

Disambiguate by alt text or position. User instruction「学生DAY 2」maps to the 2nd student-section image (not the 2nd image overall).

## Step 3: Replace Image src

```python
import base64, re

# Load and encode new image
with open('new_image.jpg', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

# Read HTML
with open('document.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the target img tag boundaries
pattern = r'<img class="day-img"[^>]+>'
matches = [(m.start(), m.group()) for m in re.finditer(pattern, content)]

# For index [N] — find its exact position in content
target_start = content.find('<img class="day-img"', matches[N][0] - 10)

# Find the end of this img tag (">")
alt_pos = content.find(f'alt="{ALT_TEXT}"', target_start)
gt_pos = content.find('>', alt_pos)

# Preserve alt attribute in new tag
new_img = f'<img class="day-img" src="data:image/jpeg;base64,{b64}" alt="{ALT_TEXT}">'

new_content = content[:target_start] + new_img + content[gt_pos+1:]

with open('document.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
```

### Inserting a NEW image (not replacing)

When the user wants to add an image *before* the first existing image in a section (e.g., "在最前面加一张"):

```python
import base64, re

with open('new_image.jpg', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

with open('document.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the first day-img tag in the target section
pattern = r'<img class="day-img"[^>]+>'
matches = [(m.start(), m.group()) for m in re.finditer(pattern, content)]
first_img_pos = matches[N][0]  # [N] = index of first img in this section

# Find the </div> that closes the day-header block — insert after it
day_header_end = content.rfind('</div>', 0, first_img_pos)
insert_pos = day_header_end + 6  # after the closing </div>

new_img_tag = f'\n      <img class="day-img" src="data:image/jpeg;base64,{b64}" alt="描述文字">\n'
new_content = content[:insert_pos] + new_img_tag + content[insert_pos:]

with open('document.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
```

**Key pattern:** In this HTML structure, `<div class="day-header">...</div>` is immediately followed by the first `<img class="day-img">`. The insertion point is right after the `</div>` of the header block.

### Counting images by section

When the user says "学生DAY 2两张":
- Count only student-section images (not parent-section images)
- Student section comes first in the HTML, parent section after
- The `[N]` index for `matches[N]` is the Nth image in the *entire file*, so account for section offsets

After any insertion or replacement, always re-enumerate all `day-img` tags and print a summary table with:
```python
labels = ['DAY1-抵达', 'DAY1-百度', 'DAY2①-科学馆', 'DAY2②-科学馆', ...]
for i, (pos, tag) in enumerate(matches):
    src_m = re.search(r'src="data:image/jpeg;base64,([^"]+)"', tag)
    alt_m = re.search(r'alt="([^"]*)"', tag)
    size_kb = len(src_m.group(1)) * 3 // 4 // 1024 if src_m else 0
    lbl = labels[i] if i < len(labels) else f'[{i}]'
    print(f"  [{i}] {lbl} | alt={alt_m.group(1)} | ~{size_kb}KB")
```

```python
import base64, re

# Load and encode new image
with open('new_image.jpg', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

# Read HTML
with open('document.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the target img tag boundaries
pattern = r'<img class="day-img"[^>]+>'
matches = [(m.start(), m.group()) for m in re.finditer(pattern, content)]

# For index [N] — find its exact position in content
target_start = content.find('<img class="day-img"', matches[N][0] - 10)

# Find the end of this img tag (">")
alt_pos = content.find(f'alt="{ALT_TEXT}"', target_start)
gt_pos = content.find('>', alt_pos)

# Preserve alt attribute in new tag
new_img = f'<img class="day-img" src="data:image/jpeg;base64,{b64}" alt="{ALT_TEXT}">'

new_content = content[:target_start] + new_img + content[gt_pos+1:]

with open('document.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
```

**Important:** Do NOT do string replacement of the old base64 directly — it may appear multiple times in the file. Use position-based boundaries (find `<img` start → find `>` end) to uniquely identify the tag.

## Step 4: Verification

After replacement, re-run the tag enumeration to confirm:
- Correct count of images
- Correct sizes (should increase if new image is larger)
- No duplicate/missing tags

```python
matches = [(m.start(), m.group()) for m in re.finditer(pattern, content)]
print(f"Total day-img tags: {len(matches)}")
```

## Common Pitfalls

### Index shift after inserting at the start of a section
**Problem:** After inserting a new image *before* the first existing image (e.g., "在最前面加一张"), all subsequent image indices shift by +1. A slot that was `[0]` becomes `[1]`, `[1]` becomes `[2]`, etc.
**Fix:** After any insertion, ALWAYS re-enumerate all `day-img` tags and print the full summary table before processing the next instruction. Do not assume slot numbers remain stable across operations.

### Alt text corruption during batch replacements
**Problem:** When replacing multiple images in a batch (e.g., 3 images in one session), it's easy to pass the wrong target alt to the wrong slot — especially when image sizes are similar. This silently corrupts the alt attribute mapping.
**Fix:** After each individual replacement, immediately verify the alt value matches the intended slot. Log both the image file (e.g., `img_c`) and the target slot `[N]` with its new alt attribute. If the user specifies "P1-DAY4, P2-DAY3, P3-DAY2", write those directly into the replacement code:
```python
replacements = [
    ('img_c', 11, 'P1-DAY4太平山'),  # ('file', slot_index, 'alt_text')
    ('img_d', 9,  'P2-DAY3'),
    ('img_e', 10, 'P3-DAY2'),
]
```

### Multiple images arrive but count mismatches user instruction
**Problem:** User says "DAY1两张" but 3 images arrive (Feishu may batch them). If you process only the first 2, the 3rd is orphaned with no slot.
**Fix:** When 3+ images arrive for a "2 images" instruction:
1. Process the confirmed ones first
2. Immediately tell the user which image(s) are unassigned and ask for placement
3. Do NOT discard the orphaned compressed images — they are saved in `/tmp/` as `img_c.jpg`, `img_d.jpg`, `img_e.jpg`

### Multiple identical placeholder base64 strings
**Problem:** The same gray placeholder image may appear in the HTML with identical base64 content across many slots. Simple string replacement of the old base64 replaces ALL copies.
**Fix:** Use position-based boundaries — find the specific `pos` from the matches list, search backward from that position to the unique `<img` tag start, then forward to the `>` end.

### PIL not available
**Symptom:** `ModuleNotFoundError: No module named 'PIL'`
**Fix:** Use `ffmpeg -vf "scale=W:-1" -q:v 2` instead. Never try to pip install Pillow in the sandbox environment.

### Image too large for vision API (>20MB base64)
**Symptom:** `Image too large for vision API: base64 payload is X MB (limit 20 MB)`
**Fix:** Compress first → `ffmpeg -i large.png -vf "scale=1200:-1" -q:v 2 -update 1 -y /tmp/compressed.jpg`

### Multiple identical img tags
**Problem:** When the same placeholder image (e.g., a gray box) appears multiple times, simple string replacement replaces all of them.
**Fix:** Use position-based replacement — find the specific `pos` from the matches list, then search backward from that position to find the unique `<img` tag start.

### Images arrive via Feishu and are cached locally
When the user sends "「这是学生DAY 1的图片，替换到DAY 1位置」" with an image attachment:
1. The image appears NOT to arrive via standard message attachment — vision_analyze can't see it in the message
2. The image IS saved to `/home/agentuser/.hermes/image_cache/img_*.jpg` — check this directory
3. These cached files are often **massive PNGs** (8MB–20MB, 8640×4860 or larger) directly from phones
4. Always check `file` and `ls -lh` on cached images before attempting to use them
5. Feishu cache filenames use pattern `img_<hash>.jpg` regardless of actual format (often PNG)

**Pattern for receiving images from Feishu:**
```
用户消息: 「这是XXX，替换到YYY」
AI收到: vision_analyze says no image / image not visible
实际情况: image saved at /home/agentuser/.hermes/image_cache/img_<hash>.jpg
处理: terminal → file / ls -lh → ffmpeg compress → execute_code replace
```

### Multiple images in one instruction
When the user sends two images for the same section (e.g., "DAY 2两张"):
- Each image arrives as a separate Feishu message
- Each message creates a separate cache file
- Process each image individually (compress → replace)
- After processing all images for a section, re-verify the full image list

## Delivering Large HTML Files to the User

When the HTML file is large (typically 5–10MB with embedded images), Feishu cannot send it as a native attachment. Alternatives:

### Option 1: Local File Path (simplest if user can access the server filesystem)
Copy to a predictable path and tell the user to open directly:
```bash
cp /path/to/file.html /tmp/启富未来-深港科创研学营（家长版）.html
```
Then send the user the path `/tmp/filename.html` to open in-browser.

### Option 2: Temporary HTTP Server (for same-network access)
```bash
# Background HTTP server
python3 -m http.server 8899 --directory /tmp/qifu_download &
# Server runs at http://<server-ip>:8899/filename.html
```
Caveat: Only works if user is on the same network (same WiFi). Not usable across NAT.

### Option 3: Convert to PDF
If the user needs a viewable file in Feishu:
- Check available tools: `which wkhtmltopdf weasyprint`
- If unavailable, this option may not be feasible in the sandbox

### Option 4: Copy to user-accessible location
If the server has a shared/network drive or the user has SFTP/SSH access:
```bash
cp file.html ~/public_html/  # if web server configured
scp file.html user@remote:/path/to/  # if SSH available
```

**Current session delivery**: copied to `/tmp/启富未来-深港科创研学营（家长版）.html` for user to access.

## P-Number Image Naming Convention

When the user sends images labeled P1, P2, P3 (e.g., "P1-DAY4, P2-DAY3, P3-DAY2"), these are **source image identifiers** provided by the user — not slot indices. Map them like this:

| User says | Means | Target slot |
|-----------|-------|-------------|
| P1-DAY4 | Image P1 goes to parent DAY4 | [N] parent DAY4 slot |
| P2-DAY3 | Image P2 goes to parent DAY3 | [N] parent DAY3 slot |
| P3-DAY2 | Image P3 goes to parent DAY2 | [N] parent DAY2 slot |
| P5+P4 (DAY1) | Two images P5 and P4 both go to DAY1 | Two slots in DAY1 section |

When multiple images arrive in one batch without explicit slot instructions:
1. Compress all images first and note their sizes
2. Ask the user to specify which image goes where using P-number labels
3. Do NOT discard orphan images — they are saved in `/tmp/` as `img_c.jpg`, `img_d.jpg`, etc.

## Feishu Form → H5 Page Conversion

When the user shares a Feishu form URL (`https://*.feishu.cn/share/base/form/...`), convert it to a standalone mobile-friendly H5 page.

**Step 1: Extract form structure via browser**
```python
# Navigate to the form URL, then capture full snapshot
browser_navigate(url="https://liuyufamilyoffice.feishu.cn/share/base/form/SHARD_ID")
browser_snapshot(full=True)  # must use full=True to get all form fields
```

**Step 2: Parse field structure**
From the snapshot accessibility tree, extract all form fields:
- Numbered fields (`StaticText "1"`, `textbox`, `StaticText "孩子姓名"`)
- Radio/option fields (clickable elements with options like "男/女", "是/否")
- Dropdown fields (clickable with static options)
- Text input fields (contenteditable or textbox)
- Required fields marked with `*`

**Step 3: Generate H5 form page**
Produce a clean mobile-first HTML form with:
- Proper `<meta name="viewport" content="width=device-width, initial-scale=1">`
- Same field structure and option sets as the Feishu original
- Required field indicators preserved
- Form submission via email or webhook (Feishu doesn't expose native form submission to external pages, so either: (a) include a mailto: link with all field values, or (b) guide the user to duplicate the form in a tool that supports external submissions like Typeform/Jinshuju)

**Example extracted field structure (研学营参加人员信息收集表):**
| # | Field | Type | Required |
|---|-------|------|----------|
| 1 | 孩子姓名 | text | ✗ |
| 2 | 国籍 | radio | ✗ |
| 3 | 证件号码 | text | ✗ |
| 4 | 出生日期 | date | ✗ |
| 5 | 是否已办理港澳通行证 | radio | ✗ |
| 6 | 性别 | radio | ✗ |
| 7 | 年龄 | number | ✗ |
| 8 | 营服尺码 | radio | ✗ |
| 9 | 家长姓名 | text | ✓ |
| 10 | 家长性别 | radio | ✓ |
| 11 | 家长国籍 | radio | ✓ |
| 12 | 家长是否已办理港澳通行证 | radio | ✓ |
| 13 | 家长证件号码 | text | ✓ |
| 14 | 家长联系方式 | tel | ✓ |
| 15 | 备注 | textarea | ✗ |

**Caveat:** Feishu forms cannot be submitted programmatically from an external H5 page. The H5 page is a *抄送/信息记录* tool, not a replacement submission endpoint. Always warn the user about this limitation.

---

## Linked Files

| Type | Path | Purpose |
|------|------|---------|
| references | `references/image-compression.md` | ffmpeg compression cookbook, size targets, vision API limits |
| references | `references/itinerary-html-bugs.md` | 研学营HTML结构Bug记录、docx vs HTML内容差异、重建检查清单 |
| references | `references/qifan-html-mapping.md` | 启富未来研学营HTML图片alt→文件映射表、HTML位置信息、替换代码模板 |
| references | `references/beta2-html-notes.md` | beta_2 版本特有备注、图片路径、微信兼容方案 |
| templates | `templates/feishu-form-to-h5.html` | starter H5 form template with field structure |

## 研学营HTML图片调整工作流（启富未来专用）

用户发图片说「先调整DAY X」时，严格按以下步骤：

1. **等用户提供内容描述** — 不要假设图片内容。用户说「发你学生 DAY 1」，等用户描述DAY1包含哪些时间段/活动
2. **确认图片与alt映射** — 查 `references/qifan-html-mapping.md` 的alt→文件映射表
3. **定位插入点** — 在HTML中找到对应day-section的 `<div class="day-header">...</div>`，图片应插入其**之后**、第一个time-row pill**之前**
4. **执行替换或插入**
5. **验证** — 打印新的img标签列表，确认位置正确

### 调整图片位置的代码模式
```python
# 找到目标day-section的day-header末尾插入点
day_header_end = content.find('</div>', content.find('day-badge', content.find('DAY X')))  
insert_pos = day_header_end + 6  # after closing </div>

# 构建新img标签（带正确的src路径）
new_img = f'\n      <img class="pdf-page-img" src="/qifan/对应的resized_px.jpg" alt="对应的alt">\n'
```

### 重要：Feishu图片接收的已知限制
- 用户发图片时 vision_analyze 返回 `404 page not found`，但图片**确实**存在于 `/home/agentuser/.hermes/image_cache/img_<hash>.jpg`
- 收到此类消息时，直接用 `file` 和 `ls -lh` 检查缓存目录，不再依赖 vision_analyze
- 缓存图片往往是超大PNG（8-20MB），使用前必须用 ffmpeg 压缩 |

## File Reference

The target file for the current session was:
`/home/agentuser/.hermes/cache/documents/doc_0acf16cc2d3c_启富未来-深港科创研学营（家长版）.html`

Image compression outputs saved to `/tmp/`:
- `student_day1_final.jpg` — compressed from 16MB PNG
- `student_day2_a.jpg` / `student_day2_b.jpg` — compressed from 17MB/13MB PNG
