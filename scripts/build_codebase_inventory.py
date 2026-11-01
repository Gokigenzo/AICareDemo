"""Build a deterministic source inventory without importing application code."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', '.venv', 'venv', 'build', 'dist', 'release', 'runtime',
            '__pycache__', '.codebase-memory', 'node_modules', '.pytest_cache',
            '.cache', 'reports', 'Ultralytics'}
SUFFIXES = {'.py', '.spec', '.bat', '.ps1', '.iss', '.yml', '.yaml'}


def inventory(root):
    records = []
    errors = []
    paths = []
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(name for name in dirs if name not in EXCLUDED)
        paths.extend(Path(directory) / name for name in files)
    for path in sorted(paths):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in EXCLUDED for part in relative.parts):
            continue
        if path.suffix not in SUFFIXES and not path.name.startswith('requirements'):
            continue
        raw = path.read_bytes()
        record = {'path': relative.as_posix(), 'bytes': len(raw),
                  'sha256': hashlib.sha256(raw).hexdigest()}
        if path.suffix in {'.py', '.spec'}:
            try:
                tree = ast.parse(raw, filename=relative.as_posix())
                record['symbols'] = [{'name': node.name, 'line': node.lineno,
                                      'kind': type(node).__name__}
                                     for node in tree.body
                                     if isinstance(node, (ast.ClassDef, ast.FunctionDef,
                                                          ast.AsyncFunctionDef))]
                record['imports'] = sorted({node.module or '' for node in ast.walk(tree)
                                            if isinstance(node, ast.ImportFrom)} |
                                           {alias.name for node in ast.walk(tree)
                                            if isinstance(node, ast.Import)
                                            for alias in node.names})
            except (SyntaxError, UnicodeError) as error:
                errors.append({'path': relative.as_posix(), 'error': str(error)})
        records.append(record)
    return {'schema_version': 1, 'files': records, 'parse_errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = inventory(ROOT)
    output = ROOT / 'docs' / 'codebase_inventory.json'
    content = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.check:
        if not output.exists() or output.read_text(encoding='utf-8') != content:
            raise SystemExit('Inventory is stale; run scripts/build_codebase_inventory.py')
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding='utf-8')
    python_count = sum(row['path'].endswith('.py') for row in result['files'])
    print(f"Files: {len(result['files'])}; Python: {python_count}; parse errors: {len(result['parse_errors'])}")
    if result['parse_errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
