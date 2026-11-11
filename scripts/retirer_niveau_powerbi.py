"""Retire le niveau textuel et applique la couleur au nombre de mentions."""
import json
from pathlib import Path
racine=Path(__file__).resolve().parents[1]
visuels=racine/'dash-bnps.Report/definition/pages/29eeb45a8260ce050a2a/visuals'
p=visuels/'themes/visual.json'
d=json.loads(p.read_text(encoding='utf-8'))
q=d['visual']['query']['queryState']['Values']
q['projections']=[x for x in q['projections'] if x['queryRef']!='Mensuel.Niveau du thème']
objects=d['visual']['objects']
for x in objects.get('values',[]):
 if x.get('selector',{}).get('metadata')=='Mensuel.Niveau du thème':x['selector']['metadata']='Mensuel.Mentions négatives'
objects['columnWidth']=[x for x in objects.get('columnWidth',[]) if x.get('selector',{}).get('metadata')!='Mensuel.Niveau du thème']
for x in objects['columnWidth']:
 if x['selector']['metadata']=='Themes.Theme':x['properties']['value']['expr']['Literal']['Value']='350D'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=visuels/'legende/visual.json';d=json.loads(p.read_text(encoding='utf-8'))
for entry in d['visual'].get('objects',{}).get('general',[]):
 for paragraph in entry.get('properties',{}).get('paragraphs',[]):
  for run in paragraph.get('textRuns',[]):
   if 'isolé' in run.get('value','').lower():
    run['value']='Couleurs : jaune = 1–2 mentions négatives · orange = ≥3 · rouge = ≥3 et ≥50 % des commentaires analysables. NPS et Baromètre : période source.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(q['projections'])==3
print('Colonne Niveau retirée ; couleurs conservées sur les mentions négatives.')
