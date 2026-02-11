# 🚀 Quick Reference Card

## Git Commands

```powershell
# Initialize repository (DONE ✅)
git init
git add .
git commit -m "Initial commit"

# Create GitHub repository
gh repo create azure-finops-elite --public --source=. --remote=origin --push

# Or manually:
# 1. Create repo on github.com/new
# 2. Then run:
git remote add origin https://github.com/YOUR_USERNAME/azure-finops-elite.git
git branch -M main
git push -u origin main
```

## GitHub Sponsors Setup

1. **Enable Sponsors**: https://github.com/sponsors
2. **Edit FUNDING.yml**: Replace `YOUR_GITHUB_USERNAME` with your username
3. **Create Tiers**:
   - $5/month - Bronze
   - $25/month - Silver
   - $100/month - Gold
   - $500/month - Enterprise

## Repository Topics

```
azure finops cost-optimization cloud-governance mcp fastmcp python flask iso27001 compliance
```

## First Release

```powershell
git tag -a v1.0.0 -m "Release v1.0.0: Initial public release"
git push origin v1.0.0
```

## Files to Update

Before publishing, replace in all files:
- `YOUR_USERNAME` → your GitHub username
- `YOUR_GITHUB_USERNAME` → your GitHub username

## Checklist

- [ ] Update usernames in README.md
- [ ] Update username in FUNDING.yml
- [ ] Create GitHub repository
- [ ] Push code to GitHub
- [ ] Enable GitHub Sponsors
- [ ] Create sponsor tiers
- [ ] Add repository topics
- [ ] Create v1.0.0 release
- [ ] Share on social media

## Quick Links

- **Setup Guide**: GIT_SETUP.md
- **Contributing**: CONTRIBUTING.md
- **Sponsors**: .github/FUNDING.yml
