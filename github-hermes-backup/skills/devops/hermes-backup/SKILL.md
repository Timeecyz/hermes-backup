---
name: hermes-backup
description: Hermes backup-to-GitHub workflow — backup script management, GitHub push protection recovery, and full-skills backup strategy. Use when (1) managing or updating hermes_backup.sh, (2) troubleshooting a GitHub push failure due to secret scanning, (3) running manual backups, or (4) modifying the backup scope.
version: 1.0.0
author: Hermes Agent
platforms: [linux]
metadata:
  hermes:
    tags: [backup, github, devops, hermes-ops]
    related_skills: [git]
---

# Hermes Backup

## Overview

Backup of Hermes config, memories, and skills runs daily at 03:00 via cron job `hermes-backup-to-github` and pushes to `Timeecyz/hermes-backup`.

**Backup script:** `~/.hermes/cron/scripts/hermes_backup.sh`
**Backup repo:** `/tmp/hermes-backup-repo` (cloned from `Timeecyz/hermes-backup`)
**Backup token:** stored in script itself (HTTPS git auth)

## Backup Scope

The script archives selected Hermes directories into a timestamped `.tar.gz` and stores it in the backup repo. Archives are kept for 5 days.

**Current scope (as of 2026-06-05):**
```
MEMORY.md        — root memory
SOUL.md          — core values
AGENTS.md        — agent definitions
memories/       — USER.md + MEMORY.md (long-term memory)
config.yaml      — Hermes config
cron/jobs.json  — cron job definitions
skills/          — FULL skills directory (all skills, not hand-picked)
```

**Previous broken scope (before 2026-06-05 fix):**
```
skills/SKILL.md
skills/sales*
skills/wechat*
skills/hk-insurance*
skills/insurance*
skills/marketing*
skills/notion*
skills/微信*
```
This only backed up ~17 of ~90 skills — new skills added after the glob was written were silently missed.

**To change backup scope:** Edit the `tar` section in `hermes_backup.sh`. When adding a new skills glob, prefer `skills/` (full directory) over individual `skills/skill-name/` globs.

## Manual Backup Run

```bash
# 1. Sync the repo
cd /tmp/hermes-backup-repo
git pull origin master

# 2. Run the backup script
cd ~/.hermes/cron/scripts && bash hermes_backup.sh

# Or do it manually:
cd ~/.hermes
tar -czf /tmp/hermes_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    MEMORY.md SOUL.md AGENTS.md memories/ cron/jobs.json skills/
cp /tmp/hermes_backup_*.tar.gz /tmp/hermes-backup-repo/
cd /tmp/hermes-backup-repo
git add hermes_backup_*.tar.gz
git add memories/MEMORY.md  # always include updated memories
git commit -m "Backup $(date '+%Y-%m-%d %H:%M')"
git push origin master
```

## GitHub Push Protection — Recovery Workflow

GitHub scans commits for secrets. If a token/repo key appears in any committed file, push is rejected:

```
remote: - Push cannot contain secrets
remote:   — Push cannot contain GH Personal Access Token
remote:         path: memories/MEMORY.md:42
```

**Recovery steps:**
```bash
# 1. Reset the last commit (keep changes staged)
git reset --soft HEAD~1

# 2. Sanitize the offending file — remove or redact the token/string
#    e.g. replace "ghp_TOKEN..." with "[TOKEN REDACTED]"
vim offending_file.txt

# 3. Re-commit and push
git add offending_file.txt
git commit -m "Fix: redact secrets before push"
git push origin master
```

**Prevention:** Never write raw tokens into MEMORY.md, USER.md, or any text file that gets committed. Store tokens only in:
- The backup script (which is not committed to the backup repo)
- `~/.hermes/.env` (not tracked by git)

## Related Files

| File | Purpose |
|------|---------|
| `~/.hermes/cron/scripts/hermes_backup.sh` | The backup script |
| `/tmp/hermes-backup-repo/` | Local clone of backup repo |
| `Timeecyz/hermes-backup` | GitHub backup repository |
| `Timeecyz/-openclaw-workspace` | Separate 33MB repo for OpenClaw skills/subagents |

## Pitfalls

- **Backup repo not in sync:** `git pull` before every manual backup, otherwise `git push` fails with non-fast-forward
- **Token in committed file:** GitHub Push Protection blocks the push; use the recovery workflow above
- **Partial skills backup:** Only commits files staged with `git add`. If new skills dir is empty or the tar is incomplete, they silently don't get backed up
- **Backup script token expires:** Token is hardcoded in `hermes_backup.sh`. If push fails, check token validity at https://github.com/settings/tokens
- **Large file >100MB push rejection:** GitHub has a hard 100MB single-file limit. When a large video/mp4 exceeds this:
  1. `git reset --hard <prev-commit>` to un-stage the oversized file (the commit stays in local ref but isn't pushed)
  2. Split into 40MB parts: `split -b 40m video.mp4 video_part_`
  3. Copy parts to backup repo and commit+push separately
  4. Or push to a separate cloud storage (Baidu Netdisk, Google Drive) and store the link instead
 5. Do NOT wait for Git LFS — it requires repo admin enabling and a separate install on the client