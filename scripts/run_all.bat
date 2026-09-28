@echo off
if "%~1"=="" (echo Usage: run_all.bat C:\path\to\front_end.exe & exit /b 2)
set "EXE=%~f1"
set "ROOT=%~dp0.."
for /f "usebackq skip=1 tokens=1 delims=    " %%T in ("%ROOT%\test_index.tsv") do (
  if not exist "%ROOT%\results\%%T" mkdir "%ROOT%\results\%%T"
  copy /y "%ROOT%\fixtures\users.txt" "%ROOT%\results\%%T\users.txt" >nul
  copy /y "%ROOT%\fixtures\games.txt" "%ROOT%\results\%%T\games.txt" >nul
  copy /y "%ROOT%\fixtures\collection.txt" "%ROOT%\results\%%T\collection.txt" >nul
  pushd "%ROOT%\results\%%T"
  "%EXE%" users.txt games.txt collection.txt daily.txt < "%ROOT%\inputs\%%T.txt" > console.txt 2>&1
  if exist daily.txt fc /w daily.txt "%ROOT%\expected_daily\%%T.txt" > daily.diff
  popd
)
