@echo off
chcp 65001 >nul
rem Setup project directory structure and create empty files

echo Creating project directory structure...
if not exist "data" mkdir "data"
if not exist "logs" mkdir "logs"
if not exist "tests" mkdir "tests"
if not exist "scripts" mkdir "scripts"

rem Create empty files (preserve if already exist)
if not exist "main.py" type nul > "main.py"
if not exist "summarizer.py" type nul > "summarizer.py"
if not exist "config.py" type nul > "config.py"
if not exist "requirements.txt" type nul > "requirements.txt"
if not exist "README.md" type nul > "README.md"
if not exist "tests\test_summarizer.py" type nul > "tests\test_summarizer.py"

echo.
echo Done! Created the following:
echo - Files: main.py, summarizer.py, config.py, requirements.txt, README.md
echo - Directories: data/, logs/, tests/, scripts/
echo - Test file: tests/test_summarizer.py
echo.
pause