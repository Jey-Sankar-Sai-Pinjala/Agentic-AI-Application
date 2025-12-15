# GitHub Setup Guide

Follow these steps to push this application to GitHub:

## Step 1: Initialize Git Repository (if not already done)

```bash
git init
```

## Step 2: Add All Files

```bash
git add .
```

## Step 3: Make Initial Commit

```bash
git commit -m "Initial commit: Agentic AI Application with Planner and Executor agents"
```

## Step 4: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right
3. Select "New repository"
4. Name your repository (e.g., "ai-chatbot" or "agentic-ai-app")
5. Choose public or private
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 5: Connect Local Repository to GitHub

```bash
# Add the remote repository (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Verify the remote was added
git remote -v
```

## Step 6: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

## Important Notes

✅ **Before pushing, make sure:**
- No API keys are hardcoded (they should be in `.env` which is gitignored)
- `.env` file is NOT committed (check `.gitignore`)
- `.env.example` is included (this is safe to commit)
- All sensitive data is removed

✅ **Files that should NOT be committed:**
- `.env` (contains your API key)
- `__pycache__/` (Python cache)
- `venv/` (virtual environment)
- `*.pyc` (compiled Python files)
- Any temporary files

✅ **Files that SHOULD be committed:**
- `.env.example` (template for API key)
- All source code files
- `requirements.txt`
- `README.md`
- `.gitignore`
- `LICENSE`

## Verify Before Pushing

```bash
# Check what will be committed
git status

# Review the changes
git diff
```

## Troubleshooting

### If you get "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

### If you need to update .gitignore
```bash
# After updating .gitignore, remove tracked files
git rm -r --cached .
git add .
git commit -m "Update .gitignore"
```

### If you accidentally committed sensitive data
```bash
# Remove the file from git history (use with caution)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

## Next Steps After Pushing

1. Add a description to your GitHub repository
2. Add topics/tags (e.g., `python`, `fastapi`, `ai`, `chatbot`)
3. Consider adding GitHub Actions for CI/CD
4. Enable GitHub Pages if you want to host the UI
