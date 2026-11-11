"""Ajoute logo, pictogrammes et part de verbatims négatifs sans réinitialiser le rapport."""
import json,shutil,csv,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];report=R/'dash-bnps.Report';page=report/'definition/pages/29eeb45a8260ce050a2a';vis=page/'visuals'
backup=R/'.work_powerbi/avant_enrichissement'
if not backup.exists():
 backup.mkdir();shutil.copytree(report,backup/'Report');shutil.copytree(R/'dash-bnps.SemanticModel',backup/'SemanticModel')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def lit(v):return {'expr':{'Literal':{'Value':str(v).lower() if isinstance(v,bool) else str(v)+'D' if isinstance(v,int) else "'"+v+"'"}}}
def obj(**p):return [{'properties':p}]
def load(n):return read(vis/n/'visual.json')
def save(n,v):
 (vis/n).mkdir(exist_ok=True);write(vis/n/'visual.json',v)
f=R/'dash-bnps.SemanticModel/definition/tables/Mensuel.tmdl'
text=f.read_text(encoding='utf-8')
measures={
'Commentaires du mois':('VAR m = [Mois choisi] RETURN IF(HASONEVALUE(Magasins[Code]), CALCULATE(DISTINCTCOUNT(Verbatims[Identifiant]), Verbatims[Mois] = m))','0'),
'Commentaires analysables':('VAR m = [Mois choisi] RETURN IF(HASONEVALUE(Magasins[Code]), CALCULATE(DISTINCTCOUNT(Verbatims[Identifiant]), Verbatims[Mois] = m, Verbatims[Sentiment] <> "Non analysable"))','0'),
'Commentaires négatifs':('VAR m = [Mois choisi] RETURN IF(NOT ISBLANK([Commentaires analysables]), COALESCE(CALCULATE(DISTINCTCOUNT(Verbatims[Identifiant]), Verbatims[Mois] = m, Verbatims[Sentiment] = "Négatif"), 0))','0'),
'Part verbatims négatifs':('DIVIDE([Commentaires négatifs], [Commentaires analysables])','0.0%'),
'Détail verbatims':('IF(NOT HASONEVALUE(Magasins[Code]), "Choisir un magasin", IF(ISBLANK([Commentaires du mois]), "Aucun commentaire disponible", FORMAT([Commentaires négatifs], "0") & "/" & FORMAT([Commentaires analysables], "0") & " analysables · " & FORMAT([Commentaires du mois], "0") & " commentaires"))',None)
}
for name,(expr,fmt) in measures.items():
 if f"measure '{name}'" not in text:
  block=f"\n\tmeasure '{name}' = {expr}\n"+(f'\t\tformatString: {fmt}\n' if fmt else '')
  text=text.replace('\n\tcolumn ',block+'\n\tcolumn ',1)
f.write_text(text,encoding='utf-8')
# Six indicateurs, sans modifier les segments et leurs sélections.
for i,n in enumerate(['nps','baro','ca','freq','panier']):
 for suffix in ['', '_detail']:
  v=load(n+suffix);v['position'].update(x=24+i*261,width=247);save(n+suffix,v)
v=load('nps');v['name']='sentiment';v['position'].update(x=1329,z=22,tabOrder=22)
q=v['visual']['query']['queryState']['Values']['projections'][0]
q.update(field={'Measure':{'Expression':{'SourceRef':{'Entity':'Mensuel'}},'Property':'Part verbatims négatifs'}},queryRef='Mensuel.Part verbatims négatifs',nativeQueryRef='Part verbatims négatifs')
q.pop('displayName',None)
v['visual']['visualContainerObjects']['title']=obj(show=lit(True),text=lit('💬 Verbatims négatifs'),fontSize=lit(12))
save('sentiment',v)
v=load('nps_detail');v['name']='sentiment_detail';v['position'].update(x=1329,z=23,tabOrder=23)
q=v['visual']['query']['queryState']['Values']['projections'][0]
q.update(field={'Measure':{'Expression':{'SourceRef':{'Entity':'Mensuel'}},'Property':'Détail verbatims'}},queryRef='Mensuel.Détail verbatims',nativeQueryRef='Détail verbatims');q.pop('displayName',None);save('sentiment_detail',v)
titles={'nps':'👍 NPS · −100 à +100','baro':'★ Baromètre · −600 à +300','ca':'↗ Chiffre d’affaires','freq':'👥 Fréquentation · tickets','panier':'🛒 Panier moyen','themes':'⚑ Thèmes du mois · mentions négatives','verbatims':'💬 Verbatims du mois · les plus récents'}
for n,title in titles.items():
 v=load(n);v['visual']['visualContainerObjects']['title'][0]['properties']['text']=lit(title);save(n,v)
# Copie exacte du logo utilisateur : aucune transformation de l’image.
assets=report/'StaticResources/RegisteredResources';assets.mkdir(exist_ok=True)
source_logo=Path('C:/Users/ABDELL~1.NGA/AppData/Local/Temp/codex-clipboard-d5e1a6ce-a7ed-4d5b-8f58-c0401f817d2c.png')
if source_logo.exists():shutil.copyfile(source_logo,assets/'carrefour-market.png')
assert (assets/'carrefour-market.png').exists(), 'Logo source manquant'
r=read(report/'definition/report.json');packages=r.setdefault('resourcePackages',[])
reg=next((p for p in packages if p['name']=='RegisteredResources'),None)
if reg is None:reg={'name':'RegisteredResources','type':'RegisteredResources','items':[]};packages.append(reg)
if not any(i['name']=='carrefour-market.png' for i in reg['items']):reg['items'].append({'name':'carrefour-market.png','path':'carrefour-market.png','type':'Image'})
write(report/'definition/report.json',r)
v=load('titre');v['position'].update(x=112,width=1032);save('titre',v)
v={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json','name':'logo_market','position':{'x':24,'y':4,'width':76,'height':72,'z':24,'tabOrder':24},'visual':{'visualType':'image','objects':{'general':obj(imageUrl={'expr':{'ResourcePackageItem':{'PackageName':'RegisteredResources','PackageType':1,'ItemName':'carrefour-market.png'}}},imageScaling=lit('Fit'))},'visualContainerObjects':{'title':obj(show=lit(False)),'background':obj(show=lit(False)),'general':obj(altText=lit('Logo Carrefour Market'))}}}
save('logo_market',v)
# Vérification indépendante des comptages pour le magasin actuellement affiché.
with (R/'outputs/powerbi/Verbatims.csv').open(encoding='utf-8-sig') as src:rows=list(csv.DictReader(src))
rs=[r for r in rows if r['Code']=='780' and r['Mois']=='2026-08'];an=[r for r in rs if r['Sentiment']!='Non analysable'];neg=[r for r in an if r['Sentiment']=='Négatif']
write(R/'outputs/powerbi/controle_sentiment.json',{'magasin':'780','mois':'2026-08','commentaires':len(rs),'analysables':len(an),'negatifs':len(neg),'part':len(neg)/len(an) if an else None,'denominateur':'Commentaires non vides et analysables ; sentiments mixtes exclus du numérateur.'})
print('Logo, pictogrammes et indicateur ajoutés.',len(neg),'/',len(an))
import runpy
runpy.run_path(str(R/'scripts/retirer_niveau_powerbi.py'))
