import csv
import json
from research.evaluate import score, edit_distance

def test_edit_distance():
    assert edit_distance(['a', 'b'], ['a', 'c', 'b']) == 1

def test_score_uses_multiset_slot_matching(tmp_path):
    path = tmp_path / 'eval.csv'
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['reference', 'hypothesis', 'reference_slots', 'hypothesis_slots'])
        writer.writeheader()
        writer.writerow({
            'reference': 'call me on 15 May',
            'hypothesis': 'call me on 15 May',
            'reference_slots': json.dumps([{'type': 'date', 'value': '15 May'}, {'type': 'date', 'value': '15 May'}]),
            'hypothesis_slots': json.dumps([{'type': 'date', 'value': '15 May'}]),
        })
    result = score(path)
    assert result['WER'] == 0
    assert result['MCSP'] == 0.5
    assert result['slot_precision_micro'] == 1
    assert result['slot_recall_micro'] == 0.5
    assert result['slot_f1_micro'] == 2/3
