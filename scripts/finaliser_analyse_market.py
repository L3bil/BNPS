"""Vérifie les résultats et assemble le tableau de bord français."""
import csv, json, re
from datetime import date, timedelta
from pathlib import Path

racine=Path(__file__).resolve().parents[1]
sortie=racine/'outputs/analyse_market'
def lire(nom):
    with (sortie/nom).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
donnees=json.loads((sortie/'donnees_tableau_de_bord.json').read_text(encoding='utf-8'))
lignes=[dict(zip(donnees['colonnes'],r)) for r in donnees['observations']]
dernieres=[r for r in lignes if r['source']=='Baromètre' and r['fin']==donnees['derniere_baro']]
assert len(dernieres)==111
assert sum(r['comparaison_possible'] and r['variation_score']<=-15 for r in dernieres)==29
assert len({r['cle'] for r in lignes})==len(lignes)
assert all(r['negatifs']<=r['commentaires_analysables']<=r['commentaires'] for r in lignes)
for r in lignes:
    if r['source']=='NPS' and r['fin']==donnees['derniere_nps']:
        assert r['ca_evolution_annuelle_pct'] is None and not r['comparaison_possible']
    if r['source']=='NPS' and r['comparaison_possible']:
        assert min(r['reponses'],r['reponses_precedentes'])>=30
for r in lire('signaux_themes_historique.csv'):
    debut,fin,rd,rf=[date.fromisoformat(r[k]) for k in ('debut_recent','fin_recent','debut_reference','fin_reference')]
    assert (fin-debut).days==27 and (rf-rd).days==55 and rf+timedelta(days=1)==debut
    a,b,n,m=[int(r[k]) for k in ('mentions_negatives_recentes','mentions_negatives_reference','commentaires_recents','commentaires_reference')]
    assert n>=5 and m>=10 and 3<=a<=n and b<=m
    assert a/n-b/m>=.15-1e-12 and a/n>=2*b/m-1e-12
suivi=lire('test_chronologique_divergences.csv')
for r in suivi:
    assert r['fin_signal']<r['fin_vague_suivante']
    assert float(r['tickets_evolution_annuelle_pct'])>-5
    assert (r['nouvelle_baisse_frequentation']=='True')==(float(r['tickets_evolution_annuelle_suivante_pct'])<=-5)
for b in donnees['bilan']:
    avec=b['groupe']=='Avec signal de divergence'
    rs=[r for r in suivi if (r['signal_divergence']=='True')==avec]
    assert len(rs)==b['observations']
    assert sum(r['nouvelle_baisse_frequentation']=='True' for r in rs)==b['baisses_futures']
gabarit=(racine/'scripts/tableau_de_bord_market.fragment.html').read_text(encoding='utf-8')
fragment=gabarit.replace('__DONNEES_MARKET__',json.dumps(donnees,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
assert len(fragment.encode('utf-8'))<1_000_000
assert '__DONNEES_MARKET__' not in fragment
repertoire=Path('C:/Users/abdellah.ngar/.codex/visualizations/2026/10/27/01a17ca6-7674-7912-a27b-ddf6e6311b98')
destination=repertoire/'tableau-de-bord-market.html'
destination.write_text(fragment,encoding='utf-8')
code=re.findall(r'<script>(.*?)</script>',fragment,re.S)[0]
(sortie/'verification_interface.js').write_text(code,encoding='utf-8')
resultat={'statut':'Contrôles réussis','observations':len(lignes),'magasins_derniere_vague':len(dernieres),'controles':['Unicité magasin/source/période','Dénominateurs des commentaires','Exclusion du NPS partiel des comparaisons commerciales','Effectifs NPS minimaux','Fenêtres temporelles disjointes et seuils des signaux','Ordre chronologique et recomptage indépendant du bilan','Taille et assemblage du tableau de bord'],'taille_tableau_de_bord_octets':len(fragment.encode('utf-8'))}
(sortie/'verification_regles.json').write_text(json.dumps(resultat,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(resultat,ensure_ascii=False))
