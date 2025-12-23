# PowerShell script to push code to GitHub
# Repository: https://github.com/incidexau-source/Incidex.git

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pushing Code to GitHub" -ForegroundColor Cyan
Write-Host "Repository: incidexau-source/Incidex" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is available
$gitPath = $null
$possiblePaths = @(
    "git",
    "C:\Program Files\Git\bin\git.exe",
    "C:\Program Files (x86)\Git\bin\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\bin\git.exe"
)

foreach ($path in $possiblePaths) {
    try {
        if ($path -eq "git") {
            $result = Get-Command git -ErrorAction Stop
            $gitPath = "git"
            break
        } elseif (Test-Path $path) {
            $gitPath = $path
            break
        }
    } catch {
        continue
    }
}

if (-not $gitPath) {
    Write-Host "ERROR: Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "Or use GitHub Desktop: https://desktop.github.com/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "See PUSH_TO_GITHUB_INSTRUCTIONS.md for detailed instructions" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Git found: $gitPath" -ForegroundColor Green
Write-Host ""

# Initialize git if not already initialized
if (-not (Test-Path .git)) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    & $gitPath init
    Write-Host ""
}

# Add all files
Write-Host "Adding files to git..." -ForegroundColor Yellow
& $gitPath add .
Write-Host ""

# Check if there are changes to commit
$status = & $gitPath status --porcelain
if ($status) {
    Write-Host "Creating commit..." -ForegroundColor Yellow
    & $gitPath commit -m "Add RSS monitor system and project files"
    Write-Host ""
} else {
    Write-Host "No changes to commit." -ForegroundColor Gray
    Write-Host ""
}

# Check if remote exists
$remoteCheck = & $gitPath remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Adding Remote Repository" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Repository URL: https://github.com/incidexau-source/Incidex.git" -ForegroundColor Green
    Write-Host ""
    Write-Host "Adding remote repository..." -ForegroundColor Yellow
    & $gitPath remote add origin https://github.com/incidexau-source/Incidex.git
    Write-Host ""
} else {
    Write-Host "Remote repository already configured: $remoteCheck" -ForegroundColor Green
    Write-Host ""
}

# Set branch to main
& $gitPath branch -M main 2>$null

# Push to GitHub
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This may prompt for credentials if not already configured." -ForegroundColor Yellow
Write-Host ""

& $gitPath push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Code pushed to GitHub" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository URL: https://github.com/incidexau-source/Incidex" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://github.com/incidexau-source/Incidex/settings/secrets/actions" -ForegroundColor White
    Write-Host "2. Click 'New repository secret'" -ForegroundColor White
    Write-Host "3. Name: OPENAI_API_KEY" -ForegroundColor White
    Write-Host "4. Value: (copy from your config.py file)" -ForegroundColor White
    Write-Host "5. Go to Actions tab and test the workflow" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to push to GitHub" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "- Authentication required (you may need to set up credentials)" -ForegroundColor White
    Write-Host "- Use GitHub Desktop for easier authentication" -ForegroundColor White
    Write-Host "- Or set up Git credentials: git config --global user.name 'Your Name'" -ForegroundColor White
    Write-Host ""
}

Read-Host "Press Enter to exit"






