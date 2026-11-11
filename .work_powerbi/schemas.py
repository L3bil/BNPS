import json,urllib.request,urllib.parse,pathlib
root=pathlib.Path(__file__).parent/'schemas';root.mkdir(exist_ok=True)
seen={}
def get(url):
 url=url.split('#')[0]
 if url in seen:return
 dest=root/(url.replace('https://developer.microsoft.com/json-schemas/','').replace('/','_'))
 d=json.loads(dest.read_text()) if dest.exists() else json.load(urllib.request.urlopen(url))
 seen[url]=d;dest.write_text(json.dumps(d))
 def walk(x):
  if isinstance(x,dict):
   if '$ref' in x and not x['$ref'].startswith('#'):get(urllib.parse.urljoin(url,x['$ref']))
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(d)
get('https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json')
get('https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json')
(root/'registre.json').write_text(json.dumps(seen))
print(len(seen))
