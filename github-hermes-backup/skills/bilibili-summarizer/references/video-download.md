# Bilibili 视频下载（纯下载，不含字幕/总结）

> 本文档是 `bilibili-summarizer` 技能的补充，说明如何**仅下载视频/音频文件**，不触发完整字幕提取流程。

---

## ✅ 首选：Bilibili API + curl（无需 Cookie，1080P可用）

**实测有效（2026-06实测）** — yt-dlp 会被 B站 反爬拦412，但 Bilibili API 直连可行：

```bash
# Step 1：获取 cid
CID=$(curl -s "https://api.bilibili.com/x/player/pagelist?bvid=BV1jV4y1X7gs&jsonp=jsonp" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Referer: https://www.bilibili.com/" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['cid'])")

# Step 2：获取 1080P 直链（qn=80）
URL=$(curl -s "https://api.bilibili.com/x/player/playurl?bvid=BV1jV4y1X7gs&cid=${CID}&qn=80&fnval=0&fnver=0&fourk=1" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Referer: https://www.bilibili.com/video/BV1jV4y1X7gs" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['durl'][0]['url'])")

# Step 3：下载
curl -L -o "~/Downloads/video.mp4" "$URL" \
  -H "Referer: https://www.bilibili.com/" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  --progress-bar
```

**番剧/合集视频**（ep_id 格式）：
```bash
# Step 1：获取 season info（含 bvid + cid）
curl -s "https://api.bilibili.com/pgc/view/web/season?ep_id=755305" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Referer: https://www.bilibili.com/" \
  | python3 -c "import sys,json; d=json.load(sys.stdin)['result']['episodes'][0]; print(d['bvid'], d['cid'])"

# Step 2：用上一步的 bvid + cid 调用 playurl API（同上）
```

**画质参数**：`qn=80`=1080P，`qn=16`=360P

---

## 工具：yt-dlp（⚠️ 已翻车，记录备查）

yt-dlp 在 B站 上会触发 412 反爬，直接使用会失败。如需强制使用需加浏览器 Cookie：
```bash
yt-dlp --cookies-from-browser chrome "BV号"  # 需要已登录 Chrome
```

---

## 工具：you-get（备选）

```bash
pip install you-get
you-get "https://www.bilibili.com/video/BV1xx411c7XD"
```

---

## 触发本技能的两种场景

| 用户意图 | 使用方式 |
|----------|----------|
| 想下载视频/音频（不要求字幕/总结） | ✅ 调 Bilibili API + curl（本文档方法） |
| 想提取字幕 + 总结 + 评分 | 调 pipeline.py |