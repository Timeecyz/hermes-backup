# HTML Image Compression Reference

## Problem
Large PNG images from phones (8MB–20MB+) need to be:
1. Compressed for HTML inline base64 embedding
2. Compressed further for vision API analysis (20MB base64 limit)

## Solution: ffmpeg (always available)

```bash
# Standard compression for HTML embedding
ffmpeg -i input.png -vf "scale=1200:-1" -q:v 2 -update 1 -y output.jpg

# Higher quality for detailed images (e.g., event posters)
ffmpeg -i input.png -vf "scale=2000:-1" -q:v 2 -update 1 -y output.jpg

# Check output
file output.jpg          # Confirm it's actually JPEG
ls -lh output.jpg        # Check size
```

## Why not PIL/Pillow?
The Hermes sandbox (`/tmp/hermes_sandbox_*/`) does NOT have Pillow pre-installed. Attempts to `pip install Pillow` work in terminal but the Python kernel used by `execute_code` tool has a different environment and may not see the installed package. Always use ffmpeg.

## Image Size Targets

| Use Case | Width | Typical Output |
|----------|-------|----------------|
| Phone photo, HTML inline | 1200px | 200–500KB |
| High-quality card/banner | 2000px | 500–800KB |
| Vision API analysis | 1200px | 200–500KB |

## Vision API Size Limit
The vision_analyze tool has a ~20MB base64 payload limit. If an image+base64 exceeds this:
1. Compress with ffmpeg to `/tmp/compressed.jpg`
2. Use that path for vision_analyze
3. Then use the same compressed file for HTML embedding

## Verification Commands
```bash
# Confirm file type
file /path/to/image.jpg
# Output: JPEG image data, JFIF standard 1.02, ... 2000x1125, components 3

# Check dimensions and size
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 /path/to/image.jpg
```
