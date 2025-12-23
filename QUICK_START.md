# Quick Start - Push to GitHub

## Fastest Way: Use GitHub Desktop

1. **Download GitHub Desktop**: https://desktop.github.com/
2. **Install and sign in** with your GitHub account
3. **Add your repository**:
   - File → Add Local Repository
   - Select: `C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map`
4. **Publish to GitHub**:
   - Click "Publish repository"
   - Choose visibility (Public/Private)
   - Click "Publish Repository"

Done! 🎉

---

## Alternative: Command Line (After Installing Git)

1. **Install Git**: https://git-scm.com/download/win

2. **Run the batch script**:
   ```batch
   push_to_github.bat
   ```
   Follow the prompts - it will guide you through the process.

3. **Or run commands manually**:
   ```powershell
   git init
   git add .
   git commit -m "Add RSS monitor system"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

---

## After Pushing - Don't Forget!

1. **Add GitHub Actions Secret**:
   - Repository → Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `OPENAI_API_KEY`
   - Value: (copy from your `config.py`)

2. **Verify Workflow**:
   - Go to Actions tab
   - You should see "Daily RSS Monitor" workflow
   - Test it by clicking "Run workflow"

---

**Need detailed instructions?** See `PUSH_TO_GITHUB_INSTRUCTIONS.md`






