"""Validate documentation and immutable source snapshot; stdlib, no app imports."""
from pathlib import Path
import ast
import hashlib
import json
import platform
import re
import sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
errors=[]
checks=[]
required=['00_EXECUTIVE_SUMMARY.md','01_CODEBASE_ARCHITECTURE.md','02_TECHNOLOGY_STACK.md',
          '03_AI_MODULES.md','04_FUNCTIONAL_WORKFLOWS.md','05_DATABASE_AND_SYNC.md',
          '06_TESTING_AND_EVIDENCE.md','07_DEVELOPMENT_HISTORY.md','08_KHKT_REPORT_MAPPING.md',
          '09_MISSING_EVIDENCE_CHECKLIST.md','10_TECHNICAL_EVIDENCE_MASTER.md','evidence_manifest.json']
for name in required:
    if not (OUT/name).is_file():errors.append('Missing required file: '+name)
claims=json.loads((OUT/'evidence_manifest.json').read_text(encoding='utf-8'))
ids={c['claim_id'] for c in claims}
if len(ids)!=len(claims):errors.append('Duplicate claim_id')
allowed={'IMPLEMENTED','PARTIALLY_IMPLEMENTED','PLANNED','DEPRECATED','REMOVED','UNKNOWN'}
fields={'claim_id','claim','evidence_type','source_path','symbol','line_range','verification_method',
        'implementation_status','confidence','limitations'}

def validate_ref(c):
    p=ROOT/c['source_path']
    if not p.is_file():
        errors.append('Missing reference '+c['source_path']);return
    data=p.read_text(encoding='utf-8');n=len(data.splitlines());a,b=c['line_range']
    if not 1<=a<=b<=n:errors.append('Bad line range '+str(c))
    if p.suffix=='.py' and c['symbol']!='module':
        tree=ast.parse(data);symbols={}
        def walk(node,prefix=''):
            for item in ast.iter_child_nodes(node):
                if isinstance(item,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
                    name=prefix+item.name;symbols[name]=[item.lineno,item.end_lineno];walk(item,name+'.')
                else:walk(item,prefix)
        walk(tree)
        if symbols.get(c['symbol'])!=[a,b]:errors.append('AST symbol/span mismatch: '+c['source_path']+' '+c['symbol'])
    if c['symbol'].startswith('CREATE TABLE '):
        table=c['symbol'].removeprefix('CREATE TABLE ')
        if not re.search(r'CREATE TABLE IF NOT EXISTS\s+'+re.escape(table)+r'\s*\(', '\n'.join(data.splitlines()[a-1:b])):
            errors.append('DDL mismatch: '+table)

for c in claims:
    if not fields.issubset(c):errors.append('Missing manifest fields '+c['claim_id'])
    if c['implementation_status'] not in allowed:errors.append('Invalid status '+c['claim_id'])
    validate_ref(c)
    for e in c.get('additional_evidence',[]):validate_ref(e)
    if c['implementation_status']=='IMPLEMENTED' and not any(e['evidence_type']=='existing_test_or_runtime_artifact' for e in c.get('additional_evidence',[])):
        errors.append('IMPLEMENTED without relevant success artefact '+c['claim_id'])

documents={name:(OUT/name).read_text(encoding='utf-8') for name in required if name.endswith('.md')}
master=documents['10_TECHNICAL_EVIDENCE_MASTER.md']
for name,text in documents.items():
    lines=text.splitlines();fenced=False;top=0;diagrams=0
    for i,line in enumerate(lines):
        if line.startswith('```'):
            if line=='```mermaid':diagrams+=1
            fenced=not fenced;continue
        if not fenced and re.match(r'^#{1,6} ',line):
            if line.startswith('# '):top+=1
            if i+1<len(lines) and lines[i+1].strip():errors.append(f'Heading needs blank line: {name}:{i+1}')
        if not fenced and re.match(r'^#{7,} ',line):errors.append('Invalid heading depth '+name)
    if fenced:errors.append('Unclosed code fence '+name)
    if top!=1:errors.append('Expected one H1 '+name)
    for cid in re.findall(r'\b(?:C\d{2}|DB_[a-z_]+)\b',text):
        if cid not in ids:errors.append('Undefined claim '+cid+' in '+name)
    if name=='01_CODEBASE_ARCHITECTURE.md' and diagrams<5:errors.append('Missing required architecture diagrams')
    if name=='05_DATABASE_AND_SYNC.md' and '```mermaid\nerDiagram' not in text:errors.append('Missing ERD')
    if name!='10_TECHNICAL_EVIDENCE_MASTER.md' and name not in master:errors.append('Master missing component '+name)

# Reject credentials/contact details in the generated package. Do not print matches.
secret_patterns=[r'AIza[0-9A-Za-z_-]{20,}',r'AQ\.[0-9A-Za-z_-]{20,}',
                 r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                 r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
                 r'\b(?:09|08|07|03|05)\d{8}\b']
for p in OUT.iterdir():
    if p.suffix not in ('.md','.json'):continue
    text=p.read_text(encoding='utf-8')
    if p.suffix=='.json':
        try:json.loads(text)
        except json.JSONDecodeError:errors.append('Invalid JSON '+p.name)
    if any(re.search(pattern,text) for pattern in secret_patterns):errors.append('Potential secret/contact pattern in '+p.name)

snapshot=json.loads((OUT/'source_snapshot.json').read_text(encoding='utf-8'))
changed=[]
for name,digest in snapshot['files'].items():
    p=ROOT/name
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(name)
if changed:errors.append('Source snapshot changed outside output: '+str(changed))

# Recalculate quoted values from existing benchmark aggregates, not new experiments.
cpu=json.loads((ROOT/'reports/local_stt/cpu-final.json').read_text())
offline=json.loads((ROOT/'reports/gemini_intent/offline-benchmark.json').read_text())
live=json.loads((ROOT/'reports/gemini_intent/limited-live-benchmark.json').read_text())
if (cpu['cold_load_ms'],cpu['p50_ms'],round(cpu['p95_ms'],2),cpu['rss_bytes'],len(cpu['results']))!=(727,4642.0,6015.95,1830600704,12):errors.append('STT metric mismatch')
if (offline['total'],offline['correct'],offline['acceptance_count'],offline['acceptance_correct'],offline['unexpected_sensitive_routes'])!=(150,104,102,72,0):errors.append('Offline metric mismatch')
if [r['latency_ms'] for r in live['records']]!=[1633,1138,1562] or live['schema_success']!=3 or live['intent_correct']!=3:errors.append('Live metric mismatch')
tables=json.loads((OUT/'schema_dictionary.json').read_text())
if len(tables)!=47:errors.append('Expected 47 migration tables')
table_ids={'DB_'+t['table'] for t in tables}
if not table_ids.issubset(ids):errors.append('Missing table claim')

report=dict(audit_date='2026-10-09',outcome='PASS' if not errors else 'FAIL',
            environment=dict(python=sys.version.split()[0],platform=platform.system(),machine=platform.machine()),
            commands=['PYTHONDONTWRITEBYTECODE=1 python3 docs/khkt_technical_evidence/generate_evidence.py',
                      'PYTHONDONTWRITEBYTECODE=1 python3 docs/khkt_technical_evidence/validate_evidence.py'],
            application_tests_executed=0,external_calls=0,production_db_opened=False,
            required_files=len(required),markdown_documents=len(documents),manifest_claims=len(claims),migration_tables=len(tables),
            source_snapshot_files_checked=len(snapshot['files']),source_snapshot_changes=changed,
            checks=['Required files','JSON syntax and manifest fields','Status enum','AST symbols and line spans',
                    'Source/artefact existence','IMPLEMENTED supporting artefacts','Claim references and consolidated coverage',
                    'Markdown headings and balanced fences','Five architecture diagrams and ERD declaration',
                    'Credential/contact pattern scan in generated Markdown/JSON','Benchmark aggregate consistency','SHA-256 source snapshot'],
            errors=errors,limitations=['Static validation only; existing test logs were not rerun.',
                                     'Mermaid blocks checked structurally, not rendered by Mermaid engine.',
                                     'Pattern scan and manual review do not prove absence of every possible sensitive string.',
                                     'Snapshot covers selected code/config/dependency files; original dirty worktree was preserved.'])
(OUT/'validation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['outcome','required_files','manifest_claims','migration_tables','source_snapshot_files_checked','application_tests_executed','errors']},ensure_ascii=False))
sys.exit(1 if errors else 0)
