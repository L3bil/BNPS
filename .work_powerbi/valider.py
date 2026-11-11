import json,pathlib,jsonschema
from referencing import Registry,Resource
r=pathlib.Path(__file__).resolve().parents[1]
schemas=json.loads((r/'.work_powerbi/schemas/registre.json').read_text())
registry=Registry().with_resources((u,Resource.from_contents(d)) for u,d in schemas.items())
errors=[];n=0
for p in (r/'dash-bnps.Report/definition/pages').rglob('*.json'):
 d=json.loads(p.read_text(encoding='utf-8'));u=d.get('$schema')
 if u not in schemas:continue
 n+=1
 for e in jsonschema.Draft7Validator(schemas[u],registry=registry).iter_errors(d):errors.append(str(p)+': '+str(list(e.path))+' '+e.message[:350])
print('\n'.join(errors) if errors else f'{n} fichiers conformes aux schémas Microsoft.')
assert not errors
