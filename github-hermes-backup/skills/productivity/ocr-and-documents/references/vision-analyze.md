# Vision Analyze — Known Pitfalls & Workarounds

## Large images (>20MB, e.g. 11520×6480 PNG)

`vision_analyze` will fail with: `Image too large for vision API: base64 payload is X MB (limit 20 MB)`

**Workaround — ffmpeg resize + compress to JPEG:**

```bash
ffmpeg -i /path/to/large_image.png -vf "scale=2000:-1" -q:v 2 -update 1 -y /tmp/compressed.jpg
```

Result: 11520×6480 PNG (16MB) → 2000×1125 JPEG (~700KB), under the 20MB limit.

Flags explained:
- `-vf "scale=2000:-1"` — scale to width 2000, height auto (-1 preserves aspect ratio)
- `-q:v 2` — JPEG quality, range 1-31 (lower = better quality)
- `-update 1` — overwrite output file (single frame)
- `-y` — auto-confirm overwrite

## Local file paths not working with vision_analyze

Even after compression, passing a local path like `/tmp/compressed.jpg` sometimes returns "I don't see the image" — the tool may not route local files correctly.

**Try in order:**
1. Copy to `/tmp/` with a simple name (no special chars)
2. If still failing, the image needs to be uploaded to the agent via the native upload mechanism (user sends it directly in the chat)

**NOTE:** If the user pastes an image directly into the chat, Hermes Agent receives it and stores it in `/home/agentuser/.hermes/image_cache/`. However, `vision_analyze` with those paths may still fail. The image must be small enough to be base64'd in the API call. Large originals in the cache should be compressed before analysis.
