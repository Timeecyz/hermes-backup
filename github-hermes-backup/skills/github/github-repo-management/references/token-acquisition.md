# GitHub Token Acquisition Guide

If the user says "api怎么找" or can't access a private repo, they need a Personal Access Token (PAT).

## Steps for the User

1. GitHub → top-right avatar → **Settings**
2. Bottom left: **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. **Generate new token (classic)**
5. Required scope:
   - For private repo read: tick **`repo`** (full controls)
   - For workflow triggers only: tick **`workflow`**
6. Copy the token — it's shown only once

## Giving the Token to the Agent

The user pastes the token directly in chat. Store it in memory:

```
github_token: ghp_XXXXXXXXXXXXX
```

## Using the Token

```bash
# Clone with embedded token
git clone https://ghp_TOKEN@github.com/owner/repo.git

# API calls
curl -s -H "Authorization: token ghp_TOKEN" \
  https://api.github.com/repos/owner/repo
```

## Token Prefix Reference

| Prefix | Type |
|--------|------|
| `ghp_` | Personal Access Token (classic) |
| `github_pat_` | Fine-grained PAT (newer) |
| `ghs_` | GitHub App user-to-server token |
| `gho_` | OAuth token |

Most common in this workflow: `ghp_` classic tokens.
