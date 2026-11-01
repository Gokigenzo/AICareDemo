"""Schema migration only. Does not claim independent annotation."""
import json
from pathlib import Path

p = Path('data/video_annotations')
d = json.loads((p/'elderly_fall_ground_truth.json').read_text(encoding='utf-8'))
d.update(dataset_version='elderly-v2-draft-20261002', annotation_status='NOT VERIFIED',
         reviewers=[], adjudication=None, negative_intervals=[[0.0, 13.5]])
for subject, identity in zip(d['subjects'], ['GT_MAN', 'GT_WOMAN']):
    subject['subject_id'] = identity
    subject['legacy_label'] = subject.pop('track_id')
    subject['bbox_samples'] = []
    subject['entry_sec'] = None
    subject['exit_sec'] = None
    subject['uncertainty_sec'] = None
target = p/'elderly_fall_v2.json'
if target.exists():
    raise FileExistsError('Refusing to overwrite versioned labels; create a new version explicitly')
target.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
