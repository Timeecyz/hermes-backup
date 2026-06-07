#!/usr/bin/env python3
"""
Verified Notion block-append script for this environment.
Key findings from 2026-06-02 session:
- Python urllib SSL context causes EMPTY responses on block writes
- subprocess curl with --tlsv1.3 works reliably
- Batch ≤5 blocks per call, sleep 1s between
- Use Notion-Version: 2022-06-28 (proven stable)
- On EMPTY response, retry up to 3x with 2s delay

Usage:
  from append_blocks import append_blocks
  result = append_blocks(page_id, [block_dict, ...], token)
"""
import subprocess, json, time

TOKEN = "[NOTION_TOKEN_REDACTED]"

def h1(t): return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": t}}]}}
def h2(t): return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": t}}]}}
def h3(t): return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": [{"text": {"content": t}}]}}
def p(t):  return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": t}}]}}

def append_blocks(page_id, blocks, token=TOKEN):
    """Append blocks to a Notion page. Returns result string."""
    payload = json.dumps({"children": blocks}).encode()
    for attempt in range(3):
        r = subprocess.run(
            ["curl", "-s", "-X", "PATCH",
             f"https://api.notion.com/v1/blocks/{page_id}/children",
             "-H", f"Authorization: Bearer {token}",
             "-H", "Notion-Version: 2022-06-28",
             "-H", "Content-Type: application/json",
             "--tlsv1.3",
             "-d", payload],
            capture_output=True, text=True, timeout=60
        )
        if r.stdout.strip():
            try:
                d = json.loads(r.stdout)
                if d.get("results"):
                    return f"OK({len(d['results'])} blocks)"
                return f"ERR:{d.get('code','')}"
            except json.JSONDecodeError:
                return f"JSON ERROR: {r.stdout[:100]}"
        if attempt < 2:
            time.sleep(2)
    return "EMPTY after 3 retries"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: append_blocks.py <page_id> <block_json_file>")
        sys.exit(1)
    page_id, json_file = sys.argv[1], sys.argv[2]
    with open(json_file) as f:
        blocks = json.load(f)
    print(append_blocks(page_id, blocks))