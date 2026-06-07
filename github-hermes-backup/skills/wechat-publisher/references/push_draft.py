"""
微信公众号草稿箱推送脚本
用法: python3 push_draft.py [标题] [摘要] [正文HTML文件路径]

依赖: 标准库 urllib.request + json（无需 pip install）
凭证从 ~/.hermes/secret&API.md 读取，或硬编码 AppID/AppSecret
"""
import sys
import json
import urllib.request

APPID = "wx37f93a23f90770b4"
APPSECRET = "c5fc89db461f4de7d55b65091979ce66"

def get_token():
    r = urllib.request.urlopen(
        "https://api.weixin.qq.com/cgi-bin/token"
        "?grant_type=client_credential&appid=" + APPID
        "&secret=" + APPSECRET + "&type=stable"
    )
    return json.loads(r.read())['access_token']

def get_thumb_media_id(token):
    """从草稿箱第一篇文拿到 thumb_media_id（XDSx... 前缀）"""
    url = "https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token=" + token
    data = json.dumps({"offset": 0, "count": 1}).encode('utf-8')
    req = urllib.request.Request(url, data=data,
        headers={'Content-Type': 'application/json; charset=utf-8'})
    r = urllib.request.urlopen(req)
    result = json.loads(r.read())
    return result['item'][0]['content']['news_item'][0]['thumb_media_id']

def push_draft(token, thumb_media_id, title, digest, content, author="环球经纪人Claire"):
    article = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": content,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0
    }
    url = "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=" + token
    payload = json.dumps({"articles": [article]}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=payload,
        headers={'Content-Type': 'application/json; charset=utf-8'})
    r = urllib.request.urlopen(req)
    return json.loads(r.read())

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python3 push_draft.py [标题] [摘要] [正文HTML文件路径]")
        sys.exit(1)

    title = sys.argv[1]
    digest = sys.argv[2]
    html_path = sys.argv[3]

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    token = get_token()
    thumb = get_thumb_media_id(token)
    result = push_draft(token, thumb, title, digest, content)

    print("Result:", result)
    if 'media_id' in result:
        print("SUCCESS! media_id:", result['media_id'])
    else:
        print("FAILED:", result)