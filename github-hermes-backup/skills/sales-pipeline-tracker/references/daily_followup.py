#!/usr/bin/env python3
"""
每日待跟推送 — 读飞书客户总表，按优先级生成跟进提醒+话术
飞书多维表格: WXghb4GgCa1NO1sydjIcNCpZn2g / tblSroifTqF6xJ6w

【核心逻辑】
优先级: A类(明确需求) > B类(有意向到期) > 老客户(复购/加保) > D类(激活) > E类(破冰)
同级别内: 紧迫度高的排前面

【话术匹配规则】
talk_key = "A逼单" / "B促行动" / "老客户" / "D激活" / "E破冰"
needs = 重疾/储蓄/信托/基金 → 组合成 "A逼单-重疾" 等精准话术
无产品匹配则降级到 "A逼单-通用"
无通用版本则降级到 "D激活-通用"

【新增字段（2025-05-28）】
- 跟进记录     type=1 (多行文本)
- 下次跟进目标 type=1 (单行文本)
- 跟进紧迫度   type=3 (单选: 🔴紧急/🟡正常/🟢可放缓)
- 跟进状态     type=3 (单选: ⏳待联系/✅已跟进/🔁需要再次联系)
"""

import subprocess, json, sys
from datetime import datetime, timedelta

# ============ CONFIG ============
APP_ID     = "cli_aa9abc638cf91bb4"
APP_SECRET = "2anV19EgpXL3r14ITxgoug2yatBn2eut"
APP_TOKEN  = "WXghb4GgCa1NO1sydjIcNCpZn2g"
TABLE_ID   = "tblSroifTqF6xJ6w"
DELIVER_TO = "feishu:oc_a56f81c068904e887d22ed102283b66d"
# ================================

def get_token():
    result = subprocess.run(['curl', '-s', '-X', 'POST',
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET})],
        capture_output=True, text=True)
    return json.loads(result.stdout)['tenant_access_token']

TOKEN = get_token()

def api_get(url):
    result = subprocess.run(['curl', '-s', url, '-H', f'Authorization: Bearer {TOKEN}'], capture_output=True, text=True)
    return json.loads(result.stdout)

# ---- Talk tracks ----
TALKS = {
    "A逼单-重疾": [
        "Hi {name}，你的重疾险方案细节已经确认好了，这周签约的话，保费还没调整，要不要今天先把保单发给你看看？",
        "Hi {name}，产品本周要停售了，你的方案已经准备好了，我们把最后几个问题线上沟通一下，直接签约可以吗？",
    ],
    "A逼单-储蓄": [
        "Hi {name}，储蓄险的投保流程我已经梳理好了，你这边确认一下保额，我们今天就把合同发过来？",
        "Hi {name}，看好的那款储蓄险额度不多了，你的方案我这边优先保留着，我们今天把最后细节确认一下？",
    ],
    "A逼单-信托": [
        "Hi {name}，信托方案的法律架构已经跑通了，你这边有没有需要调整的地方？我们今天把合同细节过一遍？",
        "Hi {name}，家族信托的设立材料准备好了，这周签约的话还能赶上本季度的设立窗口期，今天聊一下？",
    ],
    "A逼单-基金": [
        "Hi {name}，这只基金这个月的封闭期快结束了，你的认购材料我这边已经收齐，我们今天把最后确认一下？",
    ],
    "A逼单-通用": [
        "Hi {name}，你的方案准备好了，我们约个时间把最后细节确认一下，这周签约没问题吧？",
    ],
    "B促行动-重疾": [
        "Hi {name}，上次聊到重疾险的保障缺口，这段时间我想了几个方案给你，有个产品细节挺适合你的情况，方便聊聊吗？",
        "Hi {name}，最近在看一个性价比不错的重疾险，核保宽松、保费结构也适合你，上次你说想再比较一下，现在有结果了吗？",
    ],
    "B促行动-储蓄": [
        "Hi {name}，之前你说想给孩子存一笔教育金，最近有一款储蓄险的irr表现很亮眼，想不想了解一下？",
        "Hi {name}，有个消息想告诉你——你之前关注的储蓄型产品最近有产品调整，收益结构更划算了，能聊两句吗？",
    ],
    "B促行动-信托": [
        "Hi {name}，家族信托的设立门槛最近有调整，起点比之前低了将近一半，我第一时间想到了你，方便聊一下吗？",
    ],
    "B促行动-基金": [
        "Hi {name}，之前你关注的那只基金，最近净值表现不错，想不想看看最新的运作情况？",
    ],
    "B促行动-通用": [
        "Hi {name}，最近怎么样？上次聊的事情我一直记着，有个更新想和你同步，方便聊两句吗？",
    ],
    "老客户-重疾加保": [
        "Hi {name}，保单年检了吗？最近刚好有个产品升级，保障范围更全了，想给你做一下保单体检，看看需不需要补强。",
    ],
    "老客户-储蓄加保": [
        "Hi {name}，你现有的储蓄险最近有个升级方案，可以提升锁定利率的机会，你当时的产品很值得加保，想聊聊吗？",
    ],
    "老客户-交叉销售": [
        "Hi {name}，最近在帮几个老客户做资产配置的综合方案，效果不错，你这边有没有考虑把保障和储蓄结合在一起规划？",
    ],
    "老客户-通用": [
        "Hi {name}，最近怎么样？一直想找机会和你聊聊，有个新的规划思路想和你分享，方便吗？",
        "Hi {name}，好久了，最近怎么样？之前帮你配的方案最近有些新的调整，想给你同步一下，有空吗？",
    ],
    "D激活-重疾": [
        "Hi {name}，好久没联系了！最近有个关于重疾险的消息想告诉你——有几款产品马上要调整保障范围了，你之前了解的那个正好在列，还想再看一下吗？",
    ],
    "D激活-储蓄": [
        "Hi {name}，好几个月没联系了，最近在看一个很不错的储蓄方案，锁定利率+现金流设计挺适合你的，要不要重新了解一下？",
        "Hi {name}，有个消息我觉得你会感兴趣——你之前了解的那款储蓄险，最近irr又上调了一些，而且额度不多了，能聊两句吗？",
    ],
    "D激活-信托": [
        "Hi {name}，好久没联系了！家族信托最近的市场动态挺有意思的，有几家银行的合作通道刚打开，你当时想了解的，现在是好时机。",
    ],
    "D激活-基金": [
        "Hi {name}，之前你关注的那只基金，最近净值表现不错，想不想看看最新的运作情况？有些配置思路想和你分享。",
    ],
    "D激活-通用": [
        "Hi {name}，最近怎么样？之前你说在考虑的事情，我一直记着。有个新的进展想告诉你，方便聊两句吗？",
        "Hi {name}，好久了，最近怎么样？有一个消息觉得你会感兴趣——关于你之前了解的那个方案，最近有挺大更新，要聊聊吗？",
    ],
    "E破冰-重疾": [
        "Hi {name}，我是启富未来的Claire，最近帮几个家庭做了重疾险的配置，保障思路挺受认可的。想找时间和你聊聊，看看有没有适合你的方案？",
    ],
    "E破冰-储蓄": [
        "Hi {name}，我是启富未来的Claire，最近帮几个家庭做了中长期的储蓄规划，反馈挺不错。想找时间和你聊聊，看看你的财务目标是什么？",
    ],
    "E破冰-信托": [
        "Hi {name}，我是启富未来的Claire，专注做中高净值家庭的资产保全和传承规划。你这边有了解过家族信托吗？想找时间和你介绍一下目前的设立流程。",
    ],
    "E破冰-基金": [
        "Hi {name}，我是启富未来的Claire，最近在帮客户做公募/私募基金的组合配置，想和你分享一下目前的思路，有兴趣吗？",
    ],
    "E破冰-通用": [
        "Hi {name}，我是启富未来的Claire，朋友介绍说你对理财规划有兴趣，想找机会和你聊聊，最近怎么样？",
        "Hi {name}，Hi，我是Claire，还记得我吗？之前聊过关于理财规划的事，一直没机会细聊，最近有空吗？",
    ],
}

def get_talk(talk_key, name, needs=''):
    """根据客户类型+需求类型匹配话术。"""
    import random
    need_key = ''
    if needs:
        if '重疾' in needs:      need_key = '重疾'
        elif '储蓄' in needs:    need_key = '储蓄'
        elif '信托' in needs:    need_key = '信托'
        elif '基金' in needs:    need_key = '基金'
    if need_key:
        specific = talk_key + '-' + need_key
        if specific in TALKS:
            return random.choice(TALKS[specific]).format(name=_clean_name(name))
    generic = talk_key + '-通用'
    if generic in TALKS:
        return random.choice(TALKS[generic]).format(name=_clean_name(name))
    return random.choice(TALKS['D激活-通用']).format(name=_clean_name(name))

def _clean_name(name):
    return name.split('-')[0].split('（')[0].strip()

def parse_field(val):
    if val is None: return ''
    if isinstance(val, list) and len(val) > 0:
        first = val[0]
        if isinstance(first, dict): return first.get('text', str(first))
        return str(first)
    if isinstance(val, dict): return val.get('text', str(val))
    return str(val)

LEVEL_TIER = {'E类': 0, 'A类': 1, 'D类': 2, 'B类': 3, 'C类': 4}
def get_tier(level_str):
    for k, v in LEVEL_TIER.items():
        if k in level_str: return v
    return 99

# ---- 数据获取 ----
all_records = []
page_token = ""
while True:
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=100"
    if page_token:
        url += f"&page_token={page_token}"
    data = api_get(url)
    items = data.get('data', {}).get('items', [])
    all_records.extend(items)
    if not data.get('data', {}).get('has_more') or not data.get('data', {}).get('page_token'):
        break
    page_token = data.get('data', {}).get('page_token')

today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
today_ts = int(today.timestamp() * 1000)

priority = []

for item in all_records:
    f = item['fields']
    level      = parse_field(f.get('未来业务价值-客户级别', ''))
    next_c     = f.get('预计下一次联系时间', '')
    name       = parse_field(f.get('昵称', '')) or parse_field(f.get('客户姓名', ''))
    needs      = parse_field(f.get('需求类型', ''))
    notes      = parse_field(f.get('备注', ''))[:30]
    tier       = get_tier(level)
    follow_rec = parse_field(f.get('跟进记录', ''))
    next_goal  = parse_field(f.get('下次跟进目标', ''))
    urgency    = parse_field(f.get('跟进紧迫度', ''))

    status = parse_field(f.get('意向状态', ''))
    if status == '成交' and tier > 1:
        continue

    push = False
    reason = ""
    talk_key = ""

    if tier == 1:
        push = True; reason = "明确需求，本周内签约"; talk_key = "A逼单"
    elif tier == 3:
        if next_c and isinstance(next_c, int) and next_c <= today_ts:
            push = True; reason = "有意向，到了跟进时间"; talk_key = "B促行动"
    elif status == '成交':
        import hashlib
        today_str = datetime.now().strftime('%Y-%m-%d')
        day_bucket = int(hashlib.md5((item['record_id'] + today_str).encode()).hexdigest()[:8], 16) % 7
        if day_bucket == 0:
            push = True; reason = "老客户，复购/加保潜力"; talk_key = "老客户"
    elif tier == 2 and status != '成交':
        push = True; reason = "联系过但没下文，激活"; talk_key = "D激活"
    elif tier == 0:
        push = True; reason = "从未联系过，新线索破冰"; talk_key = "E破冰"

    if push:
        talk = get_talk(talk_key, name, needs)
        urgency_rank = 0 if '紧急' in urgency else (1 if '正常' in urgency else 2)
        sort_key = (0 if tier == 1 else 1 if tier == 3 else 2 if status == '成交' else 3 if tier == 2 else 4)
        priority.append((sort_key, urgency_rank, tier, reason, name, talk, needs, notes, follow_rec, next_goal))

priority.sort(key=lambda x: x[0])

if not priority:
    print("[SILENT]")
    sys.exit(0)

lines = ["📋 **今日待跟客户**\n"]
for row in priority[:15]:
    sort_key, urgency_rank, tier, reason, name, talk, needs, notes, follow_rec, next_goal = row
    emoji = "🔴" if tier <= 1 else ("🟠" if tier == 2 else "🟡")
    lines.append(f"\n{emoji} **{name}**")
    lines.append(f"   {reason}")
    if needs: lines.append(f"   需求: {needs}")
    lines.append(f"   💬 {talk}")
    if follow_rec: lines.append(f"   📍 上次: {follow_rec[:40]}")
    if next_goal:  lines.append(f"   🎯 本次: {next_goal}")
    if notes:      lines.append(f"   📌 {notes}")

if len(priority) > 15:
    lines.append(f"\n➕ 还有 **{len(priority)-15}个** 客户，按下回继续...")

print("\n".join(lines))