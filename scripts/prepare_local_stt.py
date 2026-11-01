"""Explicit preparation of the upstream Vietnamese Zipformer INT8 release."""
import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path

MODEL_NAME = 'sherpa-onnx-zipformer-vi-30M-int8-2026-02-09'
MODEL_URL = f'https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{MODEL_NAME}.tar.bz2'
MODEL_FILES = ('encoder.int8.onnx', 'decoder.onnx', 'joiner.int8.onnx', 'tokens.txt')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=['zipformer-vi'], default='zipformer-vi')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or Path(__file__).resolve().parents[1] / 'data' / 'models' / MODEL_NAME
    manifest = json.loads((Path(__file__).resolve().parents[1] / 'models' / 'manifest.json').read_text(encoding='utf-8'))
    expected = {Path(m['target_path']).name: m['sha256'] for m in manifest['models'] if m.get('category') == 'speech_stt'}
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / 'model.tar.bz2'
        urllib.request.urlretrieve(MODEL_URL, archive)
        hashes = {}
        with tarfile.open(archive, 'r:bz2') as tar:
            # Only copy expected members; never extract archive paths directly.
            for name in MODEL_FILES:
                member = tar.getmember(f'{MODEL_NAME}/{name}')
                if not member.isfile():
                    raise ValueError(f'Invalid model member: {name}')
                target = output / name
                with tar.extractfile(member) as src, target.with_suffix(target.suffix + '.tmp').open('wb') as dst:
                    shutil.copyfileobj(src, dst)
                staged = target.with_suffix(target.suffix + '.tmp')
                hashes[name] = hashlib.sha256(staged.read_bytes()).hexdigest()
                if hashes[name] != expected[name]:
                    staged.unlink()
                    raise ValueError(f'Model checksum mismatch: {name}')
                staged.replace(target)
            samples = output / 'test_wavs'
            samples.mkdir(exist_ok=True)
            for member in tar.getmembers():
                if member.isfile() and member.name.startswith(f'{MODEL_NAME}/test_wavs/') and member.name.endswith('.wav'):
                    with tar.extractfile(member) as src, (samples / Path(member.name).name).open('wb') as dst:
                        shutil.copyfileobj(src, dst)
        (output / 'provenance.json').write_text(json.dumps({'source_url': MODEL_URL, 'sha256': hashes}, indent=2), encoding='utf-8')
    print(output.resolve())


if __name__ == '__main__':
    main()
