# Hermes Backup — Working Reference

## Backup Repositories

| Repo | URL | Size | Contents |
|------|-----|------|----------|
| `Timeecyz/hermes-backup` | https://github.com/Timeecyz/hermes-backup | ~1MB | Hermes config, MEMORY.md, SOUL.md, AGENTS.md, full skills tar |
| `Timeecyz/-openclaw-workspace` | https://github.com/Timeecyz/-openclaw-workspace | 33MB | OpenClaw skills, subagents, cron scripts, customer marketing materials |

**Backup token (from hermes_backup.sh):** `[GITHUB_PAT_REDACTED]`

## Manual Backup Step-by-Step (Full Log from 2026-06-05)

```
# Clone/copy backup repo locally
cd /tmp && git clone https://[TOKEN]@github.com/Timeecyz/hermes-backup.git
cd /tmp/hermes-backup-repo && git pull origin master

# Build full backup tar
cd ~/.hermes
tar -czf /tmp/hermes_backup_20260605_0724.tar.gz \
    MEMORY.md SOUL.md AGENTS.md memories/ cron/jobs.json skills/
# Result: 25MB for ~90 skills

# Copy tar to repo, stage, commit, push
cp /tmp/hermes_backup_*.tar.gz /tmp/hermes-backup-repo/
cd /tmp/hermes-backup-repo
git add hermes_backup_*.tar.gz
git add memories/MEMORY.md  # always update memories
git commit -m "Full backup YYYY-MM-DD HH:MM"
git push origin master
```

## GitHub Push Protection — Real Error (2026-06-05)

```
remote: error: GH013: Repository rule violations found for refs/heads/master.
remote:
remote: - Push cannot contain secrets
remote:   — GH Personal Access Token
remote:     path: memories/MEMORY.md:42
```

**Resolution applied:**
1. `git reset --soft HEAD~1` — undo commit, keep staged changes
2. `git add memories/MEMORY.md` — re-stage with corrected file
3. Sanitized token string in MEMORY.md
4. `git commit -m "Full backup YYYY-MM-DD"` + `git push origin master` — succeeded

## Key Lessons

- **Token in MEMORY.md is a trap.** The file gets committed and GitHub blocks it. Store tokens only in scripts or `.env`.
- **`git pull` before every manual backup.** Repo may have new commits from the cron job.
- **Full `skills/` tar is the right scope.** Previous glob-based approach silently missed new skills.
- **`git status --short` tells you what's staged.** Always check before commit.
- **`git reset --soft HEAD~1` is safe.** It undoes the commit but keeps all changes staged — perfect for post-hoc fixes.

## Local Hermes Ops Paths

| Path | Purpose |
|------|---------|
| `~/.hermes/memories/MEMORY.md` | Long-term user/operation memory |
| `~/.hermes/memories/USER.md` | User profile |
| `~/.hermes/MEMORY.md` | Root memory (symlink or copy) |
| `~/.hermes/cron/scripts/hermes_backup.sh` | The backup script |
| `~/.hermes/cron/jobs.json` | Cron job definitions |
| `~/.hermes/skills/` | All skills (~90 dirs, 67MB) |
| `~/.openclaw/workspace/` | Subagent workspace directories |
| `/tmp/hermes-backup-repo/` | Local clone of backup repo |
| `/tmp/-openclaw-workspace/` | Local clone of OpenClaw workspace repo |