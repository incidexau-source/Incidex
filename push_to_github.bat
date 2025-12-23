@echo off
REM Script to push code to GitHub
REM Make sure Git is installed first!

echo ========================================
echo Pushing Code to GitHub
echo ========================================
echo.

REM Check if git is available
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed or not in PATH
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo Or use GitHub Desktop: https://desktop.github.com/
    echo.
    echo See PUSH_TO_GITHUB_INSTRUCTIONS.md for detailed instructions
    pause
    exit /b 1
)

echo Git found!
echo.

REM Initialize git if not already initialized
if not exist .git (
    echo Initializing git repository...
    git init
    echo.
)

REM Add all files
echo Adding files to git...
git add .
echo.

REM Check if there are changes to commit
git diff --cached --quiet
if %ERRORLEVEL% EQU 0 (
    echo No changes to commit.
    echo.
) else (
    echo Creating commit...
    git commit -m "Add RSS monitor system and project files"
    echo.
)

REM Check if remote exists
git remote get-url origin >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ========================================
    echo REMOTE REPOSITORY NOT CONFIGURED
    echo ========================================
    echo.
    echo Please provide your GitHub repository URL.
    echo Format: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    echo.
    echo If you haven't created the repository yet:
    echo 1. Go to https://github.com/new
    echo 2. Create a new repository (don't initialize with README)
    echo 3. Copy the repository URL
    echo.
    echo Your repository URL: https://github.com/incidexau-source/Incidex.git
    set REPO_URL=https://github.com/incidexau-source/Incidex.git
    
    echo.
    echo Adding remote repository...
    git remote add origin %REPO_URL%
    echo.
)

REM Set branch to main
git branch -M main 2>nul

REM Push to GitHub
echo ========================================
echo Pushing to GitHub...
echo ========================================
echo.
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Code pushed to GitHub
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Go to your repository on GitHub
    echo 2. Go to Settings -^> Secrets and variables -^> Actions
    echo 3. Add OPENAI_API_KEY secret (from config.py)
    echo 4. Go to Actions tab and test the workflow
    echo.
) else (
    echo.
    echo ERROR: Failed to push to GitHub
    echo.
    echo Common issues:
    echo - Repository doesn't exist on GitHub (create it first)
    echo - Authentication required (you may need to set up credentials)
    echo - Check your repository URL is correct
    echo.
)

pause

