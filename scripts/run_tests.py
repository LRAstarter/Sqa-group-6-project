#!/usr/bin/env python3
"""Run every indexed test with fresh fixtures and compare both output files.
Requires Python 3.8+. Expected outputs are reviewed files, never regenerated here.
Only CRLF/LF differences are normalized; spaces and blank lines remain significant.
"""
import argparse
import csv
from datetime import datetime
import difflib
from pathlib import Path
import shutil
import subprocess
import sys


def normalized(path):
    return path.read_bytes().replace(b'\r\n', b'\n')


def compare(expected, actual, difference):
    if not expected.is_file() or not actual.is_file():
        difference.write_text('Missing expected or actual file.\n', encoding='utf-8')
        return False
    wanted, observed = normalized(expected), normalized(actual)
    difference.write_text(''.join(difflib.unified_diff(
        wanted.decode('utf-8', 'replace').splitlines(True),
        observed.decode('utf-8', 'replace').splitlines(True),
        fromfile=str(expected), tofile=str(actual))), encoding='utf-8')
    return wanted == observed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable', help='Path to the compiled front end')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    executable = Path(args.executable).resolve()
    if not executable.is_file():
        parser.error('Executable does not exist: ' + str(executable))
    with (root / 'test_index.tsv').open(newline='', encoding='utf-8') as stream:
        tests = list(csv.DictReader(stream, delimiter='\t'))
    identifiers = [test['ID'] for test in tests]
    if len(identifiers) != len(set(identifiers)):
        parser.error('Duplicate test IDs in test_index.tsv')
    for test in tests:
        if None in test or any(not test.get(key) for key in ['ID', 'Area', 'Intention', 'Fixture']):
            parser.error('Malformed tab-separated test index row')
    if set(identifiers) != {p.stem for p in (root / 'inputs').glob('*.txt')}:
        parser.error('Test index and input filenames do not match')
    # A unique output folder preserves earlier executions and prevents stale results.
    run = root / 'results' / datetime.now().strftime('run_%Y%m%d_%H%M%S_%f')
    run.mkdir(parents=True)
    rows = []
    for test in tests:
        name = test['ID']
        out = run / name
        out.mkdir()
        fixture = root / 'fixtures'
        if test['Fixture'] != 'base':
            fixture /= test['Fixture']
        status, returncode = 'OK', ''
        try:
            for filename in ['users.txt', 'games.txt', 'collection.txt']:
                shutil.copyfile(fixture / filename, out / filename)
            with (root / 'inputs' / (name + '.txt')).open('rb') as source, (out / 'console.txt').open('wb') as console:
                result = subprocess.run(
                    [str(executable), 'users.txt', 'games.txt', 'collection.txt', 'daily.txt'],
                    cwd=out, stdin=source, stdout=console, stderr=subprocess.STDOUT, timeout=10)
            returncode = result.returncode
            if returncode != 0:
                status = 'NONZERO_EXIT'
        except subprocess.TimeoutExpired:
            status = 'TIMEOUT'
        except OSError as error:
            status = 'RUN_ERROR'
            (out / 'run_error.txt').write_text(str(error), encoding='utf-8')
        daily_ok = compare(root / 'expected_daily' / (name + '.txt'), out / 'daily.txt', out / 'daily.diff')
        terminal_ok = compare(root / 'terminal_messages' / (name + '.txt'), out / 'console.txt', out / 'terminal.diff')
        passed = status == 'OK' and daily_ok and terminal_ok
        rows.append([name, status, returncode, 'PASS' if daily_ok else 'FAIL', 'PASS' if terminal_ok else 'FAIL', 'PASS' if passed else 'FAIL'])
        print(('PASS ' if passed else 'FAIL ') + name)
    with (run / 'summary.tsv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream, delimiter='\t')
        writer.writerow(['Test', 'Execution', 'ExitCode', 'Daily', 'Terminal', 'Overall'])
        writer.writerows(rows)
    failed = sum(row[-1] != 'PASS' for row in rows)
    print(f'{len(rows) - failed}/{len(rows)} passed; {failed} failed. Results: {run}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
