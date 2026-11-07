## Build and run on Linux or macOS

```sh
mkdir -p build
g++ -std=c++17 src/*.cpp -o build/frontend.exe
bash scripts/run_all.sh ./build/frontend
```

Requires a C++17 compiler and Python 3.8+. The macOS and Windows wrappers were not executed in this review; validation used Linux.

## Build and run on Windows Command Prompt (run all 61 automated tests).

```bat
g++ -std=c++17 src/*.cpp -o build/frontend.exe
scripts\run_all.bat "%CD%\build\frontend.exe"
```

Install Python with the `py` launcher and put g++ on PATH. From PowerShell, use `cmd /c scripts\run_all.bat "%CD%\build\frontend.exe"` after compilation.

## Interactive invocation

```sh
./build/frontend fixtures/users.txt fixtures/games.txt fixtures/collection.txt daily.txt
```

Use build\frontend.exe on Windows. Arguments are accounts, games, collection, and output daily file. Enter login, then Admin1, then logout on separate lines. End input with Ctrl+D on Unix or Ctrl+Z then Enter in Windows Command Prompt. Logout itself permits another login.

## Tests and evidence

- test_index.tsv: 61 cases with their fixture selection.
- inputs: command streams, one file per case.
- expected_daily: reviewed expected daily transactions.
- terminal_messages: complete expected terminal transcripts, including prompts.
- fixtures: base data and dedicated one_game / after_delete fixtures.
- scripts/run_tests.py: shared runner used by the .sh and .bat entry points.
- results/run\_\*: passing full-suite executions and summary.tsv.
- evidence: original files, failing run outputs, baseline.json, and change notes.

Every run gets a new results directory. A PASS requires exit code 0, a matching daily file, and a matching console transcript. Only CRLF/LF differences are normalized. Missing files, mismatches, timeouts, or nonzero exit codes fail. The runner exits 0 for a clean suite, 1 for test failures, and 2 for argument/index errors.

Original expected text used zero-filled names, incorrect account types/balances, and console phrases not emitted by the program. Repaired inputs remove unsupported refund game names and extra create credit lines. The 15-character boundary name FifteenCharName is correct and retained. No expected output is generated from actual output by the runner.

See Phase3_Failure_Report.docx for each failure and run instructions.
