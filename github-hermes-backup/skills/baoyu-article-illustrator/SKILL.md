---
name: baoyu-article-illustrator
description: Analyzes article structure, identifies positions requiring visual aids, generates illustrations with Type × Style × Palette three-dimension approach. Use when user asks to "illustrate article", "add images", "generate images for article", or "为文章配图".
version: 1.117.4
metadata:
  language: zh
  tags: [article, illustration, image-generation]
  sources:
    - https://github.com/JimLiu/baoyu-skills
---

# baoyu-article-illustrator

文章配图生成器：Type × Style × Palette 三维度体系。

## 触发条件

用户说"为文章配图"、"生成配图"、"添加插图"、"illustrate article"时使用。

## 三维度

1. **Type（内容类型）**：场景图/数据图/流程图/人物/概念图
2. **Style（艺术风格）**：手绘/扁平/科技感/水彩/版画
3. **Palette（色调）**：暖色/冷色/中性/高饱和/莫兰迪

## 输出

生成适合 豆包/即梦/DALL-E 的中文图片提示词，配合 image_generate 使用。

## 配色方案

- warm（暖调）：#F5E6D3, #E8B86D, #C47529
- mono-ink（墨水）：#1A1A2E, #F0EEE8, #4A4A5C
- macaron（马卡龙）：#F0D9E0, #D4E8C2, #C9D6EF
- neon（霓虹）：#FF6B6B, #4ECDC4, #FFE66D