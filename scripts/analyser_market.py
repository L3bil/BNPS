"""Analyse exploratoire Market, règles explicables et données du tableau de bord.

Les sorties de ce script sont en français. Aucun fichier source n'est modifié.
"""
import csv,json,re,collections,math
from datetime import date,timedelta
from pathlib import Path

RACINE=Path(__file__).resolve().parents[1]
ENTREE=RACINE/'outputs/market_analytical'
SORTIE=RACINE/'outputs/analyse_market'
SORTIE.mkdir(parents=True,exist_ok=True)
def lire(nom):
 with (ENTREE/nom).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def ecrire(nom,lignes,champs=None):
 lignes=list(lignes)
 if champs is None:champs=list(dict.fromkeys(k for r in lignes for k in r))
 with (SORTIE/nom).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=champs);w.writeheader();w.writerows(lignes)
def nombre(v):return float(v) if v not in ('',None) else None
def arr(v):return round(v,2) if v is not None else None
def nettoyer(texte):
 texte=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[courriel masqué]',texte or '')
 texte=re.sub(r'(?<!\d)(?:\+212|00212|0)[\s.\-]?[5-7](?:[\s.\-]?\d){8}(?!\d)','[téléphone masqué]',texte)
 return re.sub(r'\s+',' ',texte).strip()
def extrait(texte,limite=260):
 t=nettoyer(texte);return t if len(t)<=limite else t[:limite].rsplit(' ',1)[0]+'…'

baro=lire('barometre_market_analytical.csv');nps=lire('nps_market_analytical.csv')
alertes={r['alert_id']:r for r in lire('alerts_market.csv')}
themes=lire('alert_themes_market.csv')
indicateurs={r['indicator_id']:r['original_label'] for r in lire('barometre_indicator_dictionary.csv')}
libelles_themes={r['theme_id']:r['theme'] for r in lire('theme_dictionary.csv')}
regles={'baisse_barometre_points':15,'baisse_nps_points':10,'reponses_nps_minimum':30,'baisse_frequentation_pourcent':5,'fenetre_recente_jours':28,'reference_jours':56,'mentions_negatives_minimum':3,'verbatims_analysables_recents_minimum':5,'verbatims_analysables_reference_minimum':10,'hausse_part_points':15,'multiplicateur_part':2,'date_limite_verbatims':'2026-10-23','date_limite_transactions':'2026-10-26'}
(SORTIE/'parametres_alertes.json').write_text(json.dumps(regles,ensure_ascii=False,indent=2),encoding='utf-8')

def theme_indicateur(k):
 if 'score_global' in k or 'satisfaction_globale' in k:return None
 if any(t in k for t in ['exactitude','etiquettes']):return 'affichage_et_exactitude_des_prix'
 if 'promotion' in k:return 'promotions'
 if 'prix' in k:return 'prix_et_rapport_qualite_prix'
 if 'qualite_fraicheur' in k:return 'qualite_et_fraicheur_des_produits'
 if 'proprete' in k:return 'proprete_et_hygiene'
 if 'attente' in k:return 'attente_et_ouverture_des_caisses'
 if 'politesse' in k:return 'accueil_et_comportement_du_personnel'
 if 'apres_caisses' in k:return 'services_en_magasin'
 if 'personnel' in k:return 'disponibilite_et_competence_du_personnel'
 if any(t in k for t in ['choix','produits_habituels']):return 'disponibilite_et_choix_des_produits'
 if 'securite' in k:return 'securite'
 return 'confort_circulation_et_equipements'
ecrire('correspondance_indicateurs_themes.csv',[{'indicateur':v,'identifiant_indicateur':k,'theme_associe':libelles_themes.get(theme_indicateur(k),'Sans correspondance — indicateur global'),'nature':'Correspondance de travail à valider, pas une pondération du score global'} for k,v in indicateurs.items()])
negatifs=collections.defaultdict(list);par_magasin=collections.defaultdict(list)
for a in alertes.values():
 a['jour']=date.fromisoformat(a['participation_date']);par_magasin[a['store_id']].append(a)
for t in themes:
 if t['theme_sentiment']=='Négatif' and alertes[t['alert_id']]['overall_sentiment']!='Non analysable':negatifs[(t['store_id'],t['theme_id'])].append(alertes[t['alert_id']])
for cle in negatifs:negatifs[cle].sort(key=lambda a:a['jour'],reverse=True)

derniere_baro=max(r['period_end'] for r in baro)
derniere_nps=max(r['period_end'] for r in nps)
historique=[];details={};preuves=[];baisses=[]
for source,lignes,champ,seuil in [('Baromètre',baro,'baro_score_global',15),('NPS',nps,'nps',10)]:
 precedents={}
 for r in sorted(lignes,key=lambda x:(x['store_id'],x['period_start'])):
  cle=source+'|'+r['store_id']+'|'+r['period_id'];precedent=precedents.get(r['store_id'])
  score=nombre(r[champ]);variation=nombre(r[champ+'_change_previous_period'])
  reponses=nombre(r.get('participation_count'));reponses_prec=nombre(precedent.get('participation_count')) if precedent and source=='NPS' else None
  comparable=(source=='Baromètre' or (r['period_end']!=derniere_nps and precedent and reponses is not None and reponses_prec is not None and min(reponses,reponses_prec)>=30)) and variation is not None
  ca=nombre(r['sales_yoy_pct']);tickets=nombre(r['ticket_count_yoy_pct'])
  baisse=comparable and variation<=-seuil
  categorie='Sans déclenchement'
  if not comparable:categorie='Comparaison insuffisante'
  elif baisse and tickets is not None and tickets<=-5:categorie='Dégradation conjointe'
  elif baisse and ca is not None and ca>=0:categorie='Satisfaction en baisse, ventes en hausse'
  elif baisse:categorie='Satisfaction en baisse'
  item={'cle':cle,'source':source,'code_magasin':r['store_id'],'magasin':r['store_name'].strip(),'periode':r['period_label']+(' '+r['period_start'][:4] if source=='Baromètre' else ''),'debut':r['period_start'],'fin':r['period_end'],'score':arr(score),'variation_score':arr(variation),'ca_evolution_annuelle_pct':arr(ca),'tickets_evolution_annuelle_pct':arr(tickets),'panier_evolution_annuelle_pct':arr(nombre(r['average_basket_yoy_pct'])),'reponses':reponses,'reponses_precedentes':reponses_prec,'commentaires':int(r['alert_count']),'commentaires_analysables':int(r['alerts_analysable_count']),'negatifs':int(r['alerts_negative_count']),'perimetre_verbatims':r['alerts_id_in_reference']=='True','comparaison_possible':bool(comparable),'categorie':categorie,'groupe':r.get('cluster') or r.get('sector') or 'Non renseigné'}
  historique.append(item)
  # Détails pour la dernière vague et les deux dernières périodes NPS.
  if (source=='Baromètre' and r['period_end']==derniere_baro) or (source=='NPS' and r['period_end']>='2026-06-30'):
   debut=date.fromisoformat(r['period_start']);fin=date.fromisoformat(r['period_end'])
   bas=[]
   if source=='Baromètre':
    for k,label in indicateurs.items():
     if k in ['baro_score_global','baro_satisfaction_globale']:continue
     d=nombre(r.get(k+'_change_previous_period'));val=nombre(r.get(k));tid=theme_indicateur(k)
     if d is not None and d<0:
      commentaires=[a for a in negatifs[(r['store_id'],tid)] if debut<=a['jour']<=fin]
      bas.append({'indicateur':label,'score':arr(val),'variation':arr(d),'theme':libelles_themes.get(tid,''),'mentions_negatives':len(commentaires)})
    bas.sort(key=lambda x:x['variation'])
    baisses.extend({'code_magasin':r['store_id'],'magasin':r['store_name'].strip(),'periode':item['periode'],**v} for v in bas)
   tlist=[]
   for tid,label in libelles_themes.items():
    candidats=[a for a in negatifs[(r['store_id'],tid)] if debut<=a['jour']<=fin]
    if candidats:
     tlist.append({'theme':label,'mentions_negatives':len(candidats),'part_des_commentaires_pct':arr(100*len(candidats)/int(r['alert_count']))})
   tlist.sort(key=lambda x:-x['mentions_negatives'])
   prioritaires=list(dict.fromkeys([v['theme'] for v in bas[:3]]+[v['theme'] for v in tlist[:3]]))
   citations=[];vus=set()
   for label in prioritaires:
    tid=next((k for k,v in libelles_themes.items() if v==label),None)
    candidats=[a for a in negatifs[(r['store_id'],tid)] if debut<=a['jour']<=fin and a['alert_id'] not in vus]
    if candidats and len(citations)<3:
     a=candidats[0];vus.add(a['alert_id'])
     ev={'identifiant_alerte':a['alert_id'],'date':a['participation_date'],'theme':label,'extrait':extrait(a['verbatim'])}
     citations.append(ev);preuves.append({'source':source,'code_magasin':r['store_id'],'magasin':r['store_name'].strip(),'periode':item['periode'],**ev})
   details[cle]={'indicateurs':bas[:5],'themes':tlist[:5],'verbatims':citations}
  precedents[r['store_id']]=r
ecrire('ecarts_satisfaction_performance.csv',historique)
ecrire('baisses_indicateurs_derniere_vague.csv',baisses)
ecrire('verbatims_appui.csv',preuves)

# Signaux de thèmes : fenêtre passée de 28 jours contre les 56 jours précédents.
fin_observation=date(2026,10,23)
dernier_dimanche=fin_observation-timedelta(days=(fin_observation.weekday()+1)%7)
dates=[];jour=date(2024,4,7)
while jour<=dernier_dimanche:dates.append(jour);jour+=timedelta(days=7)
evaluations=[];signaux=[];dernier_evenement={};evenements=[]
for fin in dates:
 debut=fin-timedelta(days=27);ref_debut=debut-timedelta(days=56);ref_fin=debut-timedelta(days=1)
 for code,alist in par_magasin.items():
  recents=[a for a in alist if debut<=a['jour']<=fin and a['overall_sentiment']!='Non analysable']
  reference=[a for a in alist if ref_debut<=a['jour']<=ref_fin and a['overall_sentiment']!='Non analysable']
  if len(recents)<5 or len(reference)<10:continue
  for tid,label in libelles_themes.items():
   if tid.startswith('contenu_') or tid in ['absence_de_verbatim','experience_globale']:continue
   ar=[a for a in negatifs[(code,tid)] if debut<=a['jour']<=fin];ab=[a for a in negatifs[(code,tid)] if ref_debut<=a['jour']<=ref_fin]
   pr=len(ar)/len(recents);pb=len(ab)/len(reference)
   declenche=len(ar)>=3 and pr-pb>=.15-1e-12 and pr>=2*pb-1e-12
   if not declenche:continue
   ligne={'code_magasin':code,'magasin':recents[0]['store_name'],'theme':label,'date_evaluation':fin.isoformat(),'debut_recent':debut.isoformat(),'fin_recent':fin.isoformat(),'debut_reference':ref_debut.isoformat(),'fin_reference':ref_fin.isoformat(),'commentaires_recents':len(recents),'commentaires_reference':len(reference),'mentions_negatives_recentes':len(ar),'mentions_negatives_reference':len(ab),'part_recente_pct':arr(pr*100),'part_reference_pct':arr(pb*100),'hausse_part_points':arr((pr-pb)*100),'identifiants_appui':'|'.join(a['alert_id'] for a in ar),'extrait_appui':extrait(ar[0]['verbatim'])}
   signaux.append(ligne)
   # Écarter les répétitions hebdomadaires d'un même épisode pendant 28 jours.
   cle=(code,tid)
   if cle not in dernier_evenement or (fin-dernier_evenement[cle]).days>=28:
    dernier_evenement[cle]=fin;ev=dict(ligne)
    fin_suivante=fin+timedelta(days=28)
    futurs=[a for a in alist if fin<a['jour']<=fin_suivante and a['overall_sentiment']!='Non analysable']
    neg_futurs=[a for a in negatifs[cle] if fin<a['jour']<=fin_suivante]
    observable=fin_suivante<=fin_observation and len(futurs)>=5
    persiste=observable and len(neg_futurs)>=3 and len(neg_futurs)/len(futurs)>=pb+.10-1e-12
    ev.update({'suivi_observable':observable,'commentaires_suivants':len(futurs) if fin_suivante<=fin_observation else None,'mentions_negatives_suivantes':len(neg_futurs) if fin_suivante<=fin_observation else None,'persistance_du_theme':persiste if observable else None})
    evenements.append(ev)
champs_signal=['code_magasin','magasin','theme','date_evaluation','debut_recent','fin_recent','debut_reference','fin_reference','commentaires_recents','commentaires_reference','mentions_negatives_recentes','mentions_negatives_reference','part_recente_pct','part_reference_pct','hausse_part_points','identifiants_appui','extrait_appui']
ecrire('signaux_themes_historique.csv',signaux,champs_signal)
ecrire('episodes_themes_suivi.csv',evenements,champs_signal+['suivi_observable','commentaires_suivants','mentions_negatives_suivantes','persistance_du_theme'])
actuels=[s for s in signaux if s['date_evaluation']==dernier_dimanche.isoformat()]
ecrire('signaux_themes_derniere_evaluation.csv',actuels,champs_signal)

# Test chronologique descriptif : signal courant puis fréquentation à la vague suivante.
suivi=[];par_code=collections.defaultdict(list)
for r in historique:
 if r['source']=='Baromètre':par_code[r['code_magasin']].append(r)
for code,rs in par_code.items():
 rs.sort(key=lambda r:r['debut'])
 for r,nxt in zip(rs,rs[1:]):
  if not r['comparaison_possible'] or r['ca_evolution_annuelle_pct'] is None or nxt['tickets_evolution_annuelle_pct'] is None:continue
  if date.fromisoformat(r['fin'])+timedelta(days=1)!=date.fromisoformat(nxt['debut']):continue
  if r['tickets_evolution_annuelle_pct'] is None or r['tickets_evolution_annuelle_pct']<=-5:continue
  suivi.append({'code_magasin':code,'magasin':r['magasin'],'fin_signal':r['fin'],'fin_vague_suivante':nxt['fin'],'signal_divergence':r['variation_score']<=-15 and r['ca_evolution_annuelle_pct']>=0,'variation_score':r['variation_score'],'ca_evolution_annuelle_pct':r['ca_evolution_annuelle_pct'],'tickets_evolution_annuelle_pct':r['tickets_evolution_annuelle_pct'],'tickets_evolution_annuelle_suivante_pct':nxt['tickets_evolution_annuelle_pct'],'nouvelle_baisse_frequentation':nxt['tickets_evolution_annuelle_pct']<=-5})
ecrire('test_chronologique_divergences.csv',suivi)
groupes=[]
for present in [True,False]:
 rs=[x for x in suivi if x['signal_divergence']==present];n=sum(x['nouvelle_baisse_frequentation'] for x in rs)
 groupes.append({'groupe':'Avec signal de divergence' if present else 'Sans signal de divergence','observations':len(rs),'magasins_distincts':len(set(x['code_magasin'] for x in rs)),'baisses_futures':n,'taux_pct':arr(100*n/len(rs)) if rs else None})
ecrire('bilan_test_chronologique.csv',groupes)

# Sensibilité : nombre de cas à examiner, sans optimisation sur les résultats futurs.
sensibilite=[];derniers=[r for r in historique if r['source']=='Baromètre' and r['fin']==derniere_baro]
for seuil in [10,15,20,25]:
 candidats=[r for r in derniers if r['comparaison_possible'] and r['variation_score']<=-seuil]
 sensibilite.append({'seuil_baisse_points':seuil,'baisses_score':len(candidats),'divergences_avec_ventes_en_hausse':sum(r['ca_evolution_annuelle_pct'] is not None and r['ca_evolution_annuelle_pct']>=0 for r in candidats),'baisses_conjointes_frequentation':sum(r['tickets_evolution_annuelle_pct'] is not None and r['tickets_evolution_annuelle_pct']<=-5 for r in candidats)})
ecrire('sensibilite_seuils.csv',sensibilite)
validation=[]
for r in sorted([r for r in derniers if r['comparaison_possible'] and r['variation_score']<=-15],key=lambda x:x['variation_score'])[:20]:
 validation.append({'type_signal':r['categorie'],'code_magasin':r['code_magasin'],'magasin':r['magasin'],'periode':r['periode'],'theme':'','constat':f"Variation du score : {r['variation_score']} points ; CA annuel : {r['ca_evolution_annuelle_pct']} %",'signal_confirme_metier':'','commentaire_metier':'','action_decidee':'','responsable':'','date_revue':''})
for s in actuels:validation.append({'type_signal':'Hausse des mentions négatives','code_magasin':s['code_magasin'],'magasin':s['magasin'],'periode':s['date_evaluation'],'theme':s['theme'],'constat':f"{s['mentions_negatives_recentes']} mentions ; hausse de part : {s['hausse_part_points']} points",'signal_confirme_metier':'','commentaire_metier':'','action_decidee':'','responsable':'','date_revue':''})
ecrire('revue_metier.csv',validation)

# Sérialisation compacte pour une exploration interactive sans requête réseau.
colonnes=['cle','source','code_magasin','magasin','periode','debut','fin','score','variation_score','ca_evolution_annuelle_pct','tickets_evolution_annuelle_pct','panier_evolution_annuelle_pct','reponses','reponses_precedentes','commentaires','commentaires_analysables','negatifs','perimetre_verbatims','comparaison_possible','categorie','groupe']
donnees={'colonnes':colonnes,'observations':[[r[k] for k in colonnes] for r in historique],'details':details,'signaux':actuels,'seuils':regles,'bilan':groupes,'sensibilite':sensibilite,'derniere_baro':derniere_baro,'derniere_nps':derniere_nps,'date_signaux':dernier_dimanche.isoformat()}
(SORTIE/'donnees_tableau_de_bord.json').write_text(json.dumps(donnees,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
resume={'derniere_vague':derniere_baro,'magasins_derniere_vague':len(derniers),'baisses_15_points':sum(r['comparaison_possible'] and r['variation_score']<=-15 for r in derniers),'categories_derniere_vague':dict(collections.Counter(r['categorie'] for r in derniers)),'signaux_themes_historiques':len(signaux),'episodes_distincts':len(evenements),'episodes_suivi_observable':sum(e['suivi_observable'] for e in evenements),'episodes_theme_persistant':sum(e['persistance_du_theme'] is True for e in evenements),'signaux_themes_actuels':len(actuels),'date_evaluation':dernier_dimanche.isoformat(),'bilan_chronologique':groupes,'taille_donnees_octets':(SORTIE/'donnees_tableau_de_bord.json').stat().st_size}
(SORTIE/'synthese_chiffree.json').write_text(json.dumps(resume,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(resume,ensure_ascii=False,indent=2))
