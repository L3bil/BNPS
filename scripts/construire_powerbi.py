"""Construit la page Power BI mensuelle et son modèle importable."""
import csv,json,collections,calendar,shutil,uuid
from pathlib import Path
R=Path(__file__).resolve().parents[1];E=R/'outputs/market_analytical';O=R/'outputs/powerbi';O.mkdir(exist_ok=True)
M=R/'dash-bnps.SemanticModel/definition';P=R/'dash-bnps.Report/definition/pages/29eeb45a8260ce050a2a'
B=R/'.work_powerbi/sauvegarde_initiale'
if not B.exists():
 B.mkdir();shutil.copytree(R/'dash-bnps.Report',B/'Report');shutil.copytree(R/'dash-bnps.SemanticModel',B/'SemanticModel')
def read(n):
 with (E/n).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(n,rows):
 with (O/(n+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def num(v):return float(v) if v not in ('',None) else None
stores=read('stores_market.csv');perf={(r['store_id'],r['month']):r for r in read('monthly_performance_market.csv')}
bar=read('barometre_market_analytical.csv');nps=read('nps_market.csv');alerts=read('alerts_market.csv');themes=read('alert_themes_market.csv')
months=[f'{y}-{m:02}' for y in range(2024,2027) for m in range(1,13) if (y,m)<=(2026,10)]
monthly=[]
for s in stores:
 for mo in months:
  code=s['store_id'];p=perf.get((code,mo),{});b=next((r for r in bar if r['store_id']==code and r['period_start'][:7]<=mo<=r['period_end'][:7]),{});n=next((r for r in nps if r['store_id']==code and r['period_start'][:7]<=mo<=r['period_end'][:7]),{})
  old=perf.get((code,str(int(mo[:4])-1)+mo[4:]),{});ca=num(p.get('sales'));fr=num(p.get('ticket_count'));oc=num(old.get('sales'));of=num(old.get('ticket_count'));complete=p.get('month_complete')=='True'
  monthly.append({'Code':code,'Mois':mo,'Ordre':int(mo[:4])*12+int(mo[5:]),'CA':ca,'Tickets':fr,'Panier':ca/fr if ca is not None and fr else None,'CA_N1':oc if complete else None,'Tickets_N1':of if complete else None,'NPS':num(n.get('nps')),'Repondants':num(n.get('participation_count')),'Periode_NPS':n.get('period_label','Non disponible'),'Barometre':num(b.get('baro_score_global')),'Vague':b.get('period_label','Non disponible')+(' '+mo[:4] if b else ''),'Couverture':('CA au 26/10 · NPS et alertes au 23/10' if mo=='2026-10' else 'Mois complet'),'Perimetre_alertes':s['in_nps_market']=='True'})
write('Mensuel',monthly)
write('Magasins',[{'Code':s['store_id'],'Magasin':(s['store_name_barometre'] or s['store_name_nps']).strip()+' ('+s['store_id']+')'} for s in stores])
write('Periodes',[{'Mois':m,'Ordre':int(m[:4])*12+int(m[5:])} for m in months])
aindex={a['alert_id']:a for a in alerts};den=collections.Counter((a['store_id'],a['participation_date'][:7]) for a in alerts if a['overall_sentiment']!='Non analysable');counts=collections.defaultdict(lambda:[set(),set()])
for t in themes:
 if t['theme_id'].startswith(('absence_','contenu_')):continue
 key=(t['store_id'],t['participation_date'][:7],t['theme']);counts[key][0].add(t['alert_id'])
 if t['theme_sentiment']=='Négatif':counts[key][1].add(t['alert_id'])
write('Themes',[{'Code':k[0],'Mois':k[1],'Theme':k[2],'Mentions':len(v[0]),'Negatives':len(v[1]),'Analysables':den[k[:2]]} for k,v in counts.items()])
comments=[]
for a in alerts:
 if not a['verbatim'].strip():continue
 comments.append({'Code':a['store_id'],'Mois':a['participation_date'][:7],'Date':a['participation_date'],'Identifiant':a['alert_id'],'Sentiment':a['overall_sentiment'],'Verbatim':a['verbatim'].replace('\r',' ').replace('\n',' ')})
write('Verbatims',comments)
schemas={'Magasins':{'Code':'string','Magasin':'string'},'Periodes':{'Mois':'string','Ordre':'int64'},'Mensuel':{k:('boolean' if k=='Perimetre_alertes' else 'int64' if k=='Ordre' else 'double' if k in ['CA','Tickets','Panier','CA_N1','Tickets_N1','NPS','Repondants','Barometre'] else 'string') for k in monthly[0]},'Themes':{'Code':'string','Mois':'string','Theme':'string','Mentions':'int64','Negatives':'int64','Analysables':'int64'},'Verbatims':{k:'string' for k in comments[0]}}
measures={}
def measure(n,d,f=None):measures[n]=(d,f)
measure('Mois choisi','SELECTEDVALUE(Periodes[Mois], "2026-08")')
measure('Ordre choisi','SELECTEDVALUE(Periodes[Ordre], 24320)')
guard='HASONEVALUE(Magasins[Code])'
for name,col,agg,fmt in [('CA du mois','CA','SUM','#,0'),('Fréquentation','Tickets','SUM','#,0'),('Panier moyen','Panier','MAX','#,0.00'),('NPS du semestre','NPS','MAX','0.0'),('Score Baromètre','Barometre','MAX','0.0'),('Répondants NPS','Repondants','MAX','#,0'),('CA année précédente','CA_N1','SUM','#,0'),('Tickets année précédente','Tickets_N1','SUM','#,0')]:
 measure(name,f'VAR m = [Mois choisi] RETURN IF({guard}, CALCULATE({agg}(Mensuel[{col}]), Mensuel[Mois] = m))',fmt)
for name,col in [('Période NPS','Periode_NPS'),('Vague Baromètre','Vague'),('Couverture du mois','Couverture')]:measure(name,f'VAR m = [Mois choisi] RETURN IF({guard}, CALCULATE(SELECTEDVALUE(Mensuel[{col}]), Mensuel[Mois] = m), "Choisir un magasin")')
measure('Évolution CA annuelle','DIVIDE([CA du mois] - [CA année précédente], [CA année précédente])','+0.0%;-0.0%;0.0%')
measure('Évolution fréquentation annuelle','DIVIDE([Fréquentation] - [Tickets année précédente], [Tickets année précédente])','+0.0%;-0.0%;0.0%')
for name,col in [('CA évolution','CA'),('CA évolution N-1','CA_N1'),('Fréquentation évolution','Tickets'),('Fréquentation évolution N-1','Tickets_N1')]:measure(name,f'VAR o = MAX(Mensuel[Ordre]) RETURN IF({guard} && o <= [Ordre choisi] && o > [Ordre choisi] - 12, SUM(Mensuel[{col}]))','#,0')
for name,col in [('Mentions négatives','Negatives'),('Mentions du thème','Mentions'),('Base analysable','Analysables')]:measure(name,f'VAR m = [Mois choisi] RETURN IF({guard}, CALCULATE(MAX(Themes[{col}]), Themes[Mois] = m))','0')
measure('Part négative du thème','DIVIDE([Mentions négatives], [Base analysable])','0%')
measure('Niveau du thème','VAR n = [Mentions négatives] VAR p = [Part négative du thème] RETURN SWITCH(TRUE(), ISBLANK(n), BLANK(), n = 0, "Aucune mention négative", n < 3, "Isolé", p >= 0.5, "Prioritaire", "Récurrent")')
measure('Couleur du thème','SWITCH([Niveau du thème], "Prioritaire", "#DC3545", "Récurrent", "#F59E0B", "Isolé", "#FDE6BA", "#E6EDF5")')
measure('Commentaire du mois','IF(HASONEVALUE(Magasins[Code]) && SELECTEDVALUE(Verbatims[Mois]) = [Mois choisi], 1)')
measure('Titre de page','"Expérience client & performance | " & SELECTEDVALUE(Magasins[Magasin], "Choisir un magasin")')
measure('Détail NPS','[Période NPS] & " · " & IF(ISBLANK([Répondants NPS]), "effectif indisponible", FORMAT([Répondants NPS], "0") & " réponses")')
measure('Détail CA','IF(ISBLANK([Évolution CA annuelle]), "Comparaison annuelle indisponible", FORMAT([Évolution CA annuelle], "+0.0%;-0.0%;0.0%") & " vs même mois N-1")')
measure('Détail fréquentation','IF(ISBLANK([Évolution fréquentation annuelle]), "Comparaison annuelle indisponible", FORMAT([Évolution fréquentation annuelle], "+0.0%;-0.0%;0.0%") & " vs même mois N-1")')
measure('Détail panier','"CA / nombre de tickets"')
for table,cols in schemas.items():
 lines=[f'table {table}']
 if table=='Mensuel':
  for name,(d,f) in measures.items():
   lines += [f"\tmeasure '{name}' = {d}"]
   if f:lines += [f'\t\tformatString: {f}']
   lines+=['']
 for col,typ in cols.items():
  lines += [f'\tcolumn {col}',f'\t\tdataType: {typ}',f'\t\tsourceColumn: {col}','\t\tsummarizeBy: none','']
 types=', '.join('{"'+c+'", '+{'string':'type text','double':'type number','int64':'Int64.Type','boolean':'type logical'}[t]+'}' for c,t in cols.items())
 lines += [f'\tpartition {table} = m','\t\tmode: import','\t\tsource =','\t\t\tlet',f'\t\t\t    Source = Csv.Document(File.Contents("{(O/(table+".csv")).as_posix()}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),','\t\t\t    Entetes = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',f'\t\t\t    Types = Table.TransformColumnTypes(Entetes, {{{types}}}, "en-US")','\t\t\tin','\t\t\t    Types']
 (M/'tables').mkdir(exist_ok=True);(M/'tables'/f'{table}.tmdl').write_text('\n'.join(lines)+'\n',encoding='utf-8')
model=(M/'model.tmdl').read_text(encoding='utf-8');model=model.split('\nref table')[0]
model+='\n'+''.join(f'\nref table {t}\n' for t in schemas)
(M/'model.tmdl').write_text(model,encoding='utf-8')
(M/'relationships.tmdl').write_text('\n'.join(f'relationship {uuid.uuid5(uuid.NAMESPACE_DNS,t)}\n\tfromColumn: {t}.Code\n\ttoColumn: Magasins.Code\n' for t in ['Mensuel','Themes','Verbatims']),encoding='utf-8')
# Visuels natifs PBIR : segments, cartes, courbes et tableaux.
def lit(v):return {'expr':{'Literal':{'Value':str(v).lower() if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+v.replace("'","''")+"'"}}}
def color(v):return {'solid':{'color':lit(v)}}
def field(t,c,m=False):return {'Measure' if m else 'Column':{'Expression':{'SourceRef':{'Entity':t}},'Property':c}}
def proj(t,c,m=False):return {'field':field(t,c,m),'queryRef':t+'.'+c,'nativeQueryRef':c}
def obj(**kw):return [{'properties':kw}]
counter=0
def visual(name,typ,x,y,w,h,title='',roles=None,objects=None):
 global counter;counter+=1
 v={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json','name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':counter,'tabOrder':counter},'visual':{'visualType':typ,'drillFilterOtherVisuals':True,'visualContainerObjects':{'title':obj(show=lit(bool(title)),text=lit(title),fontColor=color('#132C50'),fontSize=lit(13)),'background':obj(show=lit(True),color=color('#FFFFFF'),transparency=lit(0)),'border':obj(show=lit(True),color=color('#E2EAF3'),radius=lit(12))}}}
 if roles:v['visual']['query']={'queryState':{r:{'projections':p} for r,p in roles.items()}}
 if objects:v['visual']['objects']=objects
 return v
visuals=[]
def save(v):visuals.append(v)
def card(name,measure,x,y,w,h,title,size=30):
 save(visual(name,'card',x,y,w,h,title,{'Values':[proj('Mensuel',measure,True)]},{'labels':obj(fontSize=lit(size),color=color('#102C52'),labelDisplayUnits=lit(1)),'categoryLabels':obj(show=lit(False))}))
card('titre','Titre de page',24,12,1120,58,'',22)
card('couverture','Couverture du mois',1156,12,420,58,'',11)
for name,table,col,x,w,value in [('magasin','Magasins','Magasin',24,900,next(s['store_name_barometre'].strip()+' (742)' for s in stores if s['store_id']=='742')),('mois','Periodes','Mois',940,636,'2026-08')]:
 f={'Version':2,'From':[{'Name':'s','Entity':table,'Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'s'}},'Property':col}}],'Values':[[{'Literal':{'Value':"'"+value+"'"}}]]}}}]}
 save(visual(name,'slicer',x,82,w,74,'Magasin' if name=='magasin' else 'Mois',{'Values':[proj(table,col)]},{'data':obj(mode=lit('Dropdown')),'selection':obj(singleSelect=lit(True),selectAllCheckboxEnabled=lit(False)),'general':obj(filter={'filter':f})}))
cards=[('nps','NPS du semestre','NPS · −100 à +100','Détail NPS'),('baro','Score Baromètre','Baromètre · −600 à +300','Vague Baromètre'),('ca','CA du mois','Chiffre d’affaires','Détail CA'),('freq','Fréquentation','Fréquentation · tickets','Détail fréquentation'),('panier','Panier moyen','Panier moyen','Détail panier')]
for i,(id,m,title,sub) in enumerate(cards):
 x=24+i*313
 card(id,m,x,174,300,118,title)
 card(id+'_detail',sub,x,296,300,48,'',10)
for id,ms,title,x in [('courbe_ca',['CA évolution','CA évolution N-1'],'Évolution du CA · 12 mois',24),('courbe_freq',['Fréquentation évolution','Fréquentation évolution N-1'],'Évolution de la fréquentation · 12 mois',808)]:
 v=visual(id,'lineChart',x,362,768,270,title,{'Category':[proj('Mensuel','Mois')],'Y':[proj('Mensuel',m,True) for m in ms]},{'categoryAxis':obj(show=lit(True)),'valueAxis':obj(show=lit(True)),'legend':obj(show=lit(True)),'dataPoint':[{'properties':{'fill':color(c)},'selector':{'metadata':'Mensuel.'+m}} for m,c in zip(ms,['#087BEE','#A5B9D0'])]})
 v['visual']['query']['sortDefinition']={'sort':[{'field':field('Mensuel','Mois'),'direction':'Ascending'}]};save(v)
format_theme={'selector':{'metadata':'Mensuel.Niveau du thème'},'properties':{'styleBackColor':{'solid':{'color':{'expr':field('Mensuel','Couleur du thème',True)}}}}}
v=visual('themes','tableEx',24,650,610,300,'Thèmes du mois · mentions négatives',{'Values':[proj('Themes','Theme')]+[proj('Mensuel',m,True) for m in ['Mentions négatives','Part négative du thème','Niveau du thème']]},{'grid':obj(gridVertical=lit(False),rowPadding=lit(6)),'columnFormatting':[format_theme],'total':obj(totals=lit(False))})
v['visual']['query']['sortDefinition']={'sort':[{'field':field('Mensuel','Mentions négatives',True),'direction':'Descending'}]};save(v)
v=visual('verbatims','tableEx',650,650,926,300,'Verbatims du mois · les plus récents en premier',{'Values':[proj('Verbatims',c) for c in ['Date','Sentiment','Verbatim']]},{'grid':obj(gridVertical=lit(False),rowPadding=lit(8)),'values':obj(wordWrap=lit(True),fontSize=lit(11)),'total':obj(totals=lit(False))})
v['visual']['query']['sortDefinition']={'sort':[{'field':field('Verbatims','Date'),'direction':'Descending'}]}
v['filterConfig']={'filters':[{'name':'mois_des_verbatims','field':field('Mensuel','Commentaire du mois',True),'type':'Advanced','filter':{'Version':2,'From':[{'Name':'m','Entity':'Mensuel','Type':0}],'Where':[{'Condition':{'Comparison':{'ComparisonKind':0,'Left':{'Measure':{'Expression':{'SourceRef':{'Source':'m'}},'Property':'Commentaire du mois'}},'Right':{'Literal':{'Value':'1L'}}}}}]}}]};save(v)
v=visual('legende','textbox',24,962,1552,48,objects={'general':obj(paragraphs=[{'textRuns':[{'value':'Thèmes : isolé = 1–2 mentions négatives · récurrent = ≥3 · prioritaire = ≥3 et ≥50 % des alertes analysables. Scores NPS et Baromètre : période source, pas mesure mensuelle.','textStyle':{'fontSize':'10pt','color':'#536A85'}}]}])});save(v)
for v in visuals:
 if v['visual']['visualType']=='slicer':
  v['visual']['objects']['header']=obj(show=lit(False))
 if v['visual']['visualType']=='lineChart':
  v['visual']['visualContainerObjects']['subTitle']=obj(show=lit(False))
 if v['name']=='themes':
  ob=v['visual']['objects'];ob.pop('columnFormatting',None)
  ob['values']=[{'properties':{'backColor':{'solid':{'color':{'expr':field('Mensuel','Couleur du thème',True)}}}},'selector':{'data':[{'dataViewWildcard':{'matchingOption':1}}],'metadata':'Mensuel.Niveau du thème'}}]
  widths=[('Themes.Theme',240),('Mensuel.Mentions négatives',85),('Mensuel.Part négative du thème',90),('Mensuel.Niveau du thème',145)]
  ob['columnWidth']=[{'properties':{'value':lit(w)},'selector':{'metadata':c}} for c,w in widths]
  for p,label in zip(v['visual']['query']['queryState']['Values']['projections'],['Thème','Négatifs','Part','Niveau']):p['displayName']=label
 if v['name']=='verbatims':
  v['visual']['objects']['columnWidth']=[{'properties':{'value':lit(w)},'selector':{'metadata':'Verbatims.'+c}} for c,w in [('Date',100),('Sentiment',105),('Verbatim',650)]]
 d=P/'visuals'/v['name'];d.mkdir(parents=True,exist_ok=True);(d/'visual.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
page=json.loads((P/'page.json').read_text());page.update(displayName='Vue mensuelle magasin',width=1600,height=1024,objects={'background':obj(color=color('#F3F7FC'),transparency=lit(0))})
(P/'page.json').write_text(json.dumps(page,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(monthly)==len(stores)*len(months)
assert len({(r['Code'],r['Mois']) for r in monthly})==len(monthly)
(O/'controle_construction.json').write_text(json.dumps({'magasins':len(stores),'mois':len(months),'lignes_mensuelles':len(monthly),'visuels':len(visuals),'mesures':len(measures)},indent=2))
print('Modèle et page construits :',len(visuals),'visuels,',len(measures),'mesures.')
import runpy
runpy.run_path(str(R/'scripts/retirer_niveau_powerbi.py'))
