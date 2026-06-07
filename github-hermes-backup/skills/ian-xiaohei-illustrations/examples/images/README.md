# 注意：示例图片

由于网络限制，示例图片无法自动下载。

手动下载方式（在网络畅通的环境执行）：
```bash
cd ~/.hermes/skills/ian-xiaohei-illustrations
mkdir -p examples/images
# 在有网络的环境执行：
for img in 01-two-breakpoints.png 02-sort-by-purpose.png 03-one-fish-many-uses.png 04-handoff-path.png 05-information-well.png 06-idea-press.png 07-content-fermentation.png 08-trust-bridge.png; do
  curl -sL "https://raw.githubusercontent.com/helloianneo/ian-xiaohei-illustrations/main/examples/images/${img}" -o "examples/images/${img}"
done
```

或者访问 GitHub 手动下载：
https://github.com/helloianneo/ian-xiaohei-illustrations/tree/main/examples/images