# 昊总学校参赛项目 — Dragon Boat Festival (2026-06)

> 昊总参赛项目「用英语讲好中国故事」，主题：端午/屈原，时长2分40秒，6月7日截止。

## 项目文件位置
```
/home/agentuser/haozong_presentation/
├── animation.html          # 动画预览版（浏览器打开，自动播放+字幕，2分40秒）
├── haozong_dragonboat.pptx # 静态PPT版（6页，红金主题，适合投影演示）
├── make_pptx.py            # PPT生成脚本
└── index.html              # 静态幻灯片版（可翻页）
```

## 制作流程（下次参考）

1. **确认主题** → 昊总自选端午（喜欢的内容讲起来才有感情）
2. **写英文脚本** → 按时间轴分配台词，控制总时长
3. **生成PPT** → 用 `make_pptx.py`（调用 system Python: `/usr/bin/python3`）
4. **转视频** → 用户用电脑Chrome打开PPT → F5全屏演示 → 录屏导出MP4

**重要：WeChat无法直接打开HTML文件**，不能作为最终提交格式。MP4是学校要求的最终格式。

## 关键技术点

### python-pptx 在 system Python
```bash
/usr/bin/python3 -m pip install python-pptx --break-system-packages
# 运行脚本用:
/usr/bin/python3 /path/to/make_pptx.py
```
**不要用 Hermes venv Python**（`~/.hermes/hermes-agent/venv/bin/python3`）——它没有pip模块。

### PPT设计规范
- 尺寸：13.33 × 7.5 英寸（标准宽屏）
- 主色：深红 `#8B0000` + 金色 `#D4AF37`
- 字体：Georgia（英文）
- 6页结构：封面 → 人物介绍 → 事件时间线 → 高潮场景 → 纪念习俗 → 结尾

## 学校比赛要求（2026 成华嘉祥）
- 时长：不超过3分钟（中段组）
- 格式：MP4，720P以上
- 禁止出现：个人姓名、学校名、区名
- 截止：6月7日交给班主任英语老师
- 评分维度：中国特色/中国精神/中国智慧

## 英文脚本核心句型（昊总可直接用）

**开场：**
> "Hi everyone! Today I want to tell you about a special day in China — the Dragon Boat Festival."

**屈原介绍：**
> "More than 2,000 years ago, there lived a great man in China. His name was Qu Yuan."

**投江：**
> "One morning, Qu Yuan walked to the Miluo River. He was 62 years old. He looked at the water... and he jumped in."

**纪念：**
> "Today, we race dragon boats. We eat zongzi. We hang wormwood on our doors. We remember Qu Yuan every year."

**结尾升华：**
> "In China, we say — 'We never forget the people who love our country.' This is our story. Thank you!"