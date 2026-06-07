# fal.ai 下载：terminal curl 优先原则

## 关键规则
在 execute_code 的 sandbox 环境中，`urllib.request.urlretrieve()` 下载 fal.ai 图片会超时挂死。
**永远用 `terminal` 工具的 `curl` 下载 fal.ai 图片**。

## 正确流程
```bash
# Step 1: fal.ai 生成图片（submit + poll）→ 得到 URL
curl -s --max-time 25 -o /tmp/fal_cover.jpg "https://v3b.fal.media/files/xxx.jpg"

# Step 2: 上传到微信永久素材
TOKEN=$(curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx37f93a23f90770b4&secret=c5fc89db461f4de7d55b65091979ce66" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -s -F "media=@/tmp/fal_cover.jpg" \
  "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=$TOKEN&type=thumb"
# 返回 {"media_id":"XDSxRVK2ZHBjglHZA5gSc...",...}
```

## 根本原因
sandbox 对外网 HTTP 有严格的连接限制，urllib 在 execute_code 里握手慢。**不是网络问题，是 sandbox 代理行为**。

## 教训
- 图片下载 → 用 terminal 工具的 curl
- 推送草稿/Notion 写入 → 用 execute_code 的 urllib
- 两者不要混用