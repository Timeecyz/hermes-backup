# 启富未来·研学营 HTML 图片映射规则

## 文件结构
- 源HTML: `/home/agentuser/.hermes/cache/documents/doc_f34ce55de05f_启富未来-研学营-beta版本(2).html`
- 输出HTML: `/home/agentuser/.hermes/hermes-agent/web/public/qifan/启富未来-研学营-beta版本_2_.html`
- 图片目录: `/home/agentuser/.hermes/hermes-agent/web/public/qifan/resized_p5.jpg ~ resized_p16.jpg`

## 图片alt属性 → 文件名 映射表

| alt属性 | 对应文件 | 说明 |
|---------|---------|------|
| 学生DAY1-上 | resized_p5.jpg | 学生DAY1上1 |
| 学生DAY1-下 | resized_p6.jpg | 学生DAY1上2 |
| 学生DAY2-上 | resized_p7.jpg | 学生DAY2上1 |
| 学生DAY2-下 | resized_p8.jpg | 学生DAY2上2 |
| 学生DAY3-上 | resized_p9.jpg | 学生DAY3上1 |
| 学生DAY3-下 | resized_p10.jpg | 学生DAY3上2 |
| 学生DAY4-上 | resized_p11.jpg | 学生DAY4上1 |
| 学生DAY4-下 | resized_p12.jpg | 学生DAY4下1 |
| 家长DAY1-上 | resized_p13.jpg | 家长DAY1上1 |
| 家长DAY1-下 | resized_p14.jpg | 家长DAY1上2 |
| 家长DAY2-1张 | resized_p15.jpg | 家长DAY2 |
| 家长DAY3-1张 | resized_p16.jpg | 家长DAY3 |
| 家长DAY4-1张 | resized_p16.jpg | 家长DAY4（复用p16）|

## HTML结构关键位置
- 学生行程section: 约 char 7877 ~ 832548
- 家长行程section: 约 char 832548 ~ end
- 13个 `<img class="pdf-page-img">` 标签，按出现顺序依次对应上述alt映射

## 替换方法
```python
import re

html_path = "/home/agentuser/.hermes/cache/documents/doc_f34ce55de05f_启富未来-研学营-beta版本(2).html"
output_path = "/home/agentuser/.hermes/hermes-agent/web/public/qifan/启富未来-研学营-beta版本_2_.html"

alt_to_file = {
    "学生DAY1-上": "resized_p5.jpg",
    "学生DAY1-下": "resized_p6.jpg",
    "学生DAY2-上": "resized_p7.jpg",
    "学生DAY2-下": "resized_p8.jpg",
    "学生DAY3-上": "resized_p9.jpg",
    "学生DAY3-下": "resized_p10.jpg",
    "学生DAY4-上": "resized_p11.jpg",
    "学生DAY4-下": "resized_p12.jpg",
    "家长DAY1-上": "resized_p13.jpg",
    "家长DAY1-下": "resized_p14.jpg",
    "家长DAY2-1张": "resized_p15.jpg",
    "家长DAY3-1张": "resized_p16.jpg",
    "家长DAY4-1张": "resized_p16.jpg",
}

with open(html_path, 'r') as f:
    content = f.read()

# 按顺序替换所有base64 src为文件URL
base64_pattern = re.compile(r'src="data:image/jpeg;base64,[A-Za-z0-9+/=]+"')
matches = list(base64_pattern.finditer(content))
alt_data = [(m.start(), m.group(1)) for m in re.finditer(r'alt="([^"]+)"', content)]

# 找每个base64最近的alt
def find_nearest_alt(b64_pos):
    best = None
    for alt_pos, alt_val in alt_data:
        if alt_pos < b64_pos:
            best = alt_val
    return best

# 逆序替换（避免offset偏移）
for i, m in enumerate(reversed(matches)):
    idx = len(matches) - 1 - i
    nearest_alt = find_nearest_alt(m.start())
    fname = alt_to_file.get(nearest_alt, f"resized_p{idx+5}.jpg")
    new_content = content[:m.start()] + f'src="/qifan/{fname}"' + content[m.end():]

with open(output_path, 'w') as f:
    f.write(new_content)
```

## 注意事项
- 家长DAY4-1张 复用了 resized_p16.jpg（因为只有12个文件却有13个槽位）
- 图片插入位置规则：每个day的图片放在每天行程的最上方（day-header之后）
- 图片src路径统一使用 `/qifan/文件名` 的相对URL格式