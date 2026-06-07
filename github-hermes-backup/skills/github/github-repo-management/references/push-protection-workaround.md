# GitHub Push Protection — Working Around Blocked Pushes

## Problem

GitHub's secret scanning and push protection can reject a push if committed files contain API tokens, keys, or credentials — even in JSON config files, even in `.env` files that were never meant to be committed.

**Error seen:**
```
remote: error: GH013: Repository rule violations found for refs/heads/master.
remote: - Push cannot contain secrets
remote:   — Notion API Token ——
remote:   — commit: abc123
remote:     path: some_file.json:121
```

## Resolution Steps

### 1. Redact the credentials in the offending file(s)

```python
import re

with open('problem_file.json') as f:
    content = f.read()

# Redact common credential patterns
redacted = re.sub(r'"token":\s*"[^"]+"', '"token": "[REDACTED]"', content)
redacted = re.sub(r'"api[_-]?key":\s*"[^"]+"', '"api_key": "[REDACTED]"', redacted)
redacted = re.sub(r'"api[_-]?secret":\s*"[^"]+"', '"api_secret": "[REDACTED]"', redacted)
redacted = re.sub(r'NOTION_API_KEY=[^\s,"]+', 'NOTION_API_KEY=[REDACTED]', redacted)

with open('problem_file.json', 'w') as f:
    f.write(redacted)
```

### 2. Amend the commit with the redacted content

```bash
git add problem_file.json
git commit --amend  # reuse previous commit message, just update content
GIT_ASKPASS=echo git push
```

**Important:** `git commit --amend` rewrites the commit history. If the commit was already pushed to a shared branch, use `--force-with-lease` instead of `--force`.

### 3. Alternative: Allow the secret via GitHub's secret scanning UI

If the secret is a real credential that needs to be in the repo, follow the URL in the error message:
```
https://github.com/{owner}/{repo}/security/secret-scanning/unblock-secret/{secret_id}
```

## Prevention

- **Before committing config files containing credentials**, do a pre-commit scan:
  ```bash
  grep -rE '(token|api_key|secret|password|credential)' --include="*.json" --include="*.yaml" .
  ```
- **Never commit `.env` files** — keep them in `.gitignore` and reference them via environment variables
- **Use GitHub's "Push protection bypass"** for intentional cases, but prefer redaction for backup/archive repos
