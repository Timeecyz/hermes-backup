---
name: bilibili-video-download
description: Bilibili视频下载——通过官方API绕过yt-dlp的412反爬，获取直链后curl下载
triggers:
  - 用户要给视频链接，要下载Bilibili视频
  - 昊总参赛视频
---

# Bilibili Video Download

## 工作流

### Step 1：获取 CID
```bash
curl -s "https://api.bilibili.com/x/player/pagelist?bvid={BV号}&jsonp=jsonp" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Referer: https://www.bilibili.com/"" \
  | python3 -m json.tool
```
从返回值取 `data[0].cid`

### Step 2：调用播放地址 API
```bash
curl -s "https://api.bilibili.com/x/player/playurl?bvid={BV号}&cid={CID}&qn=80&fnval=0&fnver=0&fourk=1" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Referer: https://www.bilibili.com/video/{BV号}" \
  | python3 -m json.tool
```
- `qn=80` = 1080P高清，`qn=16` = 360P流畅
- 从 `data.durl[0].url` 取直链

### Step 3：下载
```bash
curl -L -o "/绝对路径/文件名.mp4" \
  "视频直链" \
  -H "Referer: https://www.bilibili.com/" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  --progress-bar
```

## 注意事项
- yt-dlp 会触发 B站 412 反爬，直接用 API 更稳定
- 直链有时效（deadline 参数），过期就重新调 Step 2 获取新链接
- 文件名用中文可以，但路径要绝对路径避免 shell 展开问题
- 存放目录：`~/Downloads/bilibili/`

## 番剧/课程详情页（ep_id链接）

有些B站视频是番剧/课程形式，URL 是 `bilibili.com/bangumi/play/ep755305` 而不是普通视频。

**Step 1：先查 season info 获取 bvid 和 cid**
```bash
curl -s "https://api.bilibili.com/pgc/view/web/season?ep_id={ep_id}" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Referer: https://www.bilibili.com/" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(e['bvid'], e['cid'], e['long_title']) for e in d['result']['episodes']]"
```

**Step 2：拿到 bvid 后走普通视频流程（Step 2 + Step 3）**
Referer 改为 `https://www.bilibili.com/bangumi/play/ep{ep_id}`

## 大文件上传 GitHub（>100MB）

## 大文件传输方案

GitHub 单文件硬限制 100MB，百度网盘需要 BDUSS，飞书限制约 100MB（媒体附件）。

**推荐传输优先级：**
1. **飞书直接发**（文件<100MB）
2. **飞书分卷**（100MB 文件 → 拆成 90MB + 剩余 → 发两个 .z01/.z02 → 用户用 7-Zip 解压 .z01 自动合并）
3. **GitHub backup repo**（<100MB 直接 push）
4. **百度网盘网页版**（用户上传后分享链接）
5. **transfer.sh 等海外服务**（国内网络不通，已验证失败）

### 飞书分卷操作流程
```python
import zipfile, os

src = '/path/to/video.mp4'
base = '/path/to/video'
chunk_size = 90 * 1024 * 1024  # 90MB

with open(src, 'rb') as f:
    part_num = 1
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        part_path = f'{base}.z{part_num:02d}'
        with open(part_path, 'wb') as out:
            out.write(chunk)
        part_num += 1
#发送所有分卷，接收方用 7-Zip 打开 .z01 解压
```

### GitHub push 失败恢复
如果 push 因文件过大被拒，先回退：
```bash
cd /tmp/hermes-backup-repo
git reset --hard<上一个成功的commit-sha>
git push origin master --force
```
**不要让 rejected commit 留在分支上**，会阻止后续所有 push。

**文件存放目录：** `~/Downloads/bilibili/`

## 提取字幕/内容
如果只需要字幕，用 `web_extract` 或加载 `bilibili-summarizer` 技能。