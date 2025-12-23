# How to Push Your Code to GitHub

Since Git command line may not be installed, here are **three easy options**:

## Option 1: Install Git for Windows (Recommended)

### Step 1: Install Git
1. Download Git from: https://git-scm.com/download/win
2. Run the installer with default settings
3. After installation, restart your terminal/PowerShell

### Step 2: Open PowerShell in your project folder
1. Right-click on your project folder
2. Select "Open in Terminal" or "Open PowerShell window here"
3. Or navigate to the folder:
   ```powershell
   cd C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map
   ```

### Step 3: Initialize and Push
```powershell
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Add RSS monitor system and existing project files"

# Add your GitHub repository as remote
# REPLACE YOUR_USERNAME and YOUR_REPO_NAME with your actual GitHub details
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note**: If you haven't created the GitHub repository yet:
1. Go to https://github.com/new
2. Create a new repository (don't initialize with README)
3. Copy the repository URL it shows
4. Use that URL in the `git remote add origin` command above

---

## Option 2: Use GitHub Desktop (Easiest - No Command Line)

### Step 1: Install GitHub Desktop
1. Download from: https://desktop.github.com/
2. Install and sign in with your GitHub account

### Step 2: Add Your Repository
1. Open GitHub Desktop
2. Click **File → Add Local Repository**
3. Click **Choose** and select your project folder:
   ```
   C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map
   ```
4. Click **Add Repository**

### Step 3: Publish to GitHub
1. If repository doesn't exist on GitHub:
   - Click **Publish repository** button
   - Uncheck "Keep this code private" if you want it public
   - Click **Publish Repository**

2. If repository already exists:
   - Click **Repository → Repository Settings**
   - Click **Remote** tab
   - Paste your GitHub repository URL
   - Click **Save**
   - Click **Fetch origin**
   - Click **Push origin**

### Step 4: Commit and Push Your Changes
1. You'll see all your files listed as changes
2. Write a commit message: "Add RSS monitor system"
3. Click **Commit to main**
4. Click **Push origin** (if needed)

---

## Option 3: Upload via GitHub Website (Quick but Limited)

### Step 1: Create Repository on GitHub
1. Go to https://github.com/new
2. Name: `lgbtiq-hate-crime-map`
3. Click **Create repository**

### Step 2: Upload Files
1. After creating, you'll see "uploading an existing file" option
2. Drag and drop your entire project folder
3. Or click "uploading an existing file" and select files manually

**Note**: This method is not ideal for large projects or ongoing updates.

---

## After Pushing - Configure GitHub Actions Secret

Once your code is on GitHub:

1. **Go to your repository on GitHub**
2. **Click Settings** (top menu)
3. **Secrets and variables → Actions**
4. **Click "New repository secret"**
5. **Name**: `OPENAI_API_KEY`
6. **Value**: Copy from your `config.py` file:
   ```
   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
   ```
7. **Click "Add secret"**

---

## Verify Everything Works

1. **Check your repository**: Go to your GitHub repository page
2. **Check Actions tab**: You should see the "Daily RSS Monitor" workflow
3. **Test the workflow**: 
   - Go to Actions tab
   - Click "Daily RSS Monitor"
   - Click "Run workflow" → "Run workflow"
   - Monitor the execution

---

## Need Help?

- **Git not working?** Use GitHub Desktop (Option 2) - it's the easiest
- **Repository URL?** It will be: `https://github.com/YOUR_USERNAME/lgbtiq-hate-crime-map`
- **Having issues?** Check that all files are in the folder, including the new RSS monitor files






