"""Validate native locale data and generate the lightweight selector index."""
import json
import re
import sys
from pathlib import Path

destination = Path(sys.argv[1])
languages = ('en', 'as', 'bn', 'brx', 'doi', 'gu', 'hi', 'kn', 'ks-Arab', 'gom', 'mai',
             'ml', 'mni-Mtei', 'mr', 'ne', 'or', 'pa-Guru', 'sa', 'sat-Olck',
             'sd-Arab', 'ta', 'te', 'ur')
catalogs = {
    code: json.loads((destination / 'locales' / f'{code}.json').read_text(encoding='utf-8'))
    for code in languages
}
english = catalogs['en']
metadata = json.loads((destination / 'content.json').read_text(encoding='utf-8'))

def same_shape(reference, actual):
    if isinstance(reference, dict):
        return isinstance(actual, dict) and reference.keys() == actual.keys() and all(
            same_shape(value, actual[key]) for key, value in reference.items()
        )
    if isinstance(reference, list):
        return isinstance(actual, list) and len(reference) == len(actual) and all(
            same_shape(a, b) for a, b in zip(reference, actual)
        )
    return (isinstance(actual, str) and bool(actual.strip())
            and not re.search(r'([^\s]{2,14})\1{5,}', actual))

if {item['id'] for item in metadata['scams']} != set(english['_scams']):
    raise SystemExit('Scam metadata does not match its catalog')
if {row[0] for row in metadata['practice']} != set(english['_learn']):
    raise SystemExit('Exercise metadata does not match its catalog')

for code, lexicon in catalogs.items():
    if not same_shape({k:v for k,v in english.items() if k != '_meta'},
                      {k:v for k,v in lexicon.items() if k != '_meta'}):
        raise SystemExit(f'{code}: invalid catalog')
    if len(lexicon['_checklist']) != 12:
        raise SystemExit(f'{code}: invalid checklist size')
    for group, key in (('_ui', 'progress'), ('_native', 'dial')):
        if sorted(re.findall(r'\{\w+\}', lexicon[group][key])) != sorted(
            re.findall(r'\{\w+\}', english[group][key])
        ):
            raise SystemExit(f'{code}: invalid substitution tokens')
    if lexicon['copy108'] != 'cybercrime.gov.in' or not re.search(r'(?<!\d)1930(?!\d)', lexicon['copy1']):
        raise SystemExit(f'{code}: invalid reporting information')

(destination / 'languages.json').write_text(json.dumps({
    code: catalogs[code]['_meta']['label'] for code in languages
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
