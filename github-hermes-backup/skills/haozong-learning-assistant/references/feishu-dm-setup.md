# 昊总飞书接入排错笔记

## 现象：昊总在群组里发消息，Hermes无响应

**根因**：飞书群组和DM共享同一个session_key前缀 `feishu:dm:oc_d8b1a9b0a48a1756c84d97444b83ddb5`，导致机器人收到昊总消息时无法区分"这是昊总在学习"还是"这是蛮子在工作"。 Hermes对群组消息的路由逻辑中，群组成员的身份只记录到sender的open_id，但没有profile隔离机制，所以群组内的昊总消息被当作普通用户消息处理，但可能因为trigger/response逻辑而静默丢弃。

**解决**：昊总必须和Hermes开**独立DM**（一对一私聊），DM才有独立session。

## 飞书API查询笔记

- 查token: POST `https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal`
- 查用户: POST `https://open.feishu.cn/open-apis/contact/v3/users/find_by_mobile` body: `{"mobiles": [phone]}`
- 查DM会话列表: GET `https://open.feishu.cn/open-apis/im/v1/chats?page_size=50&chat_type=p2p`
- 查群组成员: GET `https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members`
- 查聊天记录: GET `https://open.feishu.cn/open-apis/im/v1/messages?container_id_type=chat&container_id={chat_id}`
- 昊总open_id: `ou_5c130a23cd64a3cda48ad47f8b26d7aa`
- 昊总DM chat_id: 需要单独建立DM后查询

## 正确接入流程

1. 昊总在飞书找到"蛮子のHermes"bot
2. 直接发消息（不要拉群、不要@mention）
3. bot回复即接入成功