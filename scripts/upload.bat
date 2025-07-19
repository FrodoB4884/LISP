@echo off
REM === Configure these ===
set GIT_PATH=D:\MyStuff\Git\bin
set PROJECT_PATH=D:\MyStuff\Python\Projects\LISP

REM === Add Git to PATH temporarily ===
set PATH=%GIT_PATH%;%PATH%

REM === Go to project folder ===
cd /d %PROJECT_PATH%

REM === Add and commit ===
git add .

if "%~1"=="" (
    set COMMIT_MSG=Update
) else (
    set COMMIT_MSG=%*
)

git commit -m "%COMMIT_MSG%"
git push

pause

