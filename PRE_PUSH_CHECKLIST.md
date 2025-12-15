# Pre-Push Checklist

Before pushing to GitHub, verify the following:

## ✅ Security Checks

- [ ] No API keys hardcoded in source code
- [ ] `.env` file is in `.gitignore` and NOT committed
- [ ] `.env.example` exists and is safe to commit
- [ ] No passwords or secrets in code
- [ ] No personal information in code

## ✅ File Checks

- [ ] `requirements.txt` is up to date
- [ ] `README.md` is complete and accurate
- [ ] `.gitignore` includes all necessary patterns
- [ ] `LICENSE` file exists
- [ ] All source code files are included

## ✅ Code Quality

- [ ] Code runs without errors
- [ ] No syntax errors
- [ ] Imports are correct
- [ ] No broken references

## ✅ Documentation

- [ ] README has setup instructions
- [ ] API endpoints are documented
- [ ] Installation steps are clear
- [ ] Environment variables are documented

## ✅ Git Status

Run these commands to verify:

```bash
# Check what will be committed
git status

# Review changes
git diff

# Check for large files
git ls-files | xargs ls -lh | sort -k5 -hr | head -20
```

## ✅ Test Before Pushing

```bash
# Test the application starts
python main.py

# Run tests (if available)
pytest tests/

# Check for linting errors
# (if you have a linter configured)
```

## ✅ Final Verification

- [ ] All sensitive data removed
- [ ] `.env` is NOT in git status
- [ ] Ready for public/private repository
- [ ] Commit message is clear

## Quick Commands

```bash
# See what will be committed
git status

# See what's ignored
git status --ignored

# Check for .env in tracked files
git ls-files | grep -E "\.env$"

# If .env is tracked, remove it
git rm --cached .env
```
