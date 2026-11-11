# Satisfaction → performance : résultats

**Aucun signal précurseur clair et stable ne ressort.** Les résultats ne justifient pas une alerte commerciale fondée sur ces indicateurs seuls.

| Analyse | Résultat | Effectif |
|---|---|---|
| Décalages 1–3 mois, alertes normalisées | r de −0,057 à +0,095 | 737–888 observations |
| Décalages, score global | r de −0,115 à +0,105 | 875–972 |
| Décalages, satisfaction | r de −0,011 à +0,060 | 875–972 |
| Intra-magasin, alertes | r de −0,106 à +0,040 | 459–605 |
| Intra-magasin, score global | r de −0,030 à +0,029 | 749–845 |
| Intra-magasin, satisfaction | r de −0,007 à +0,035 | 749–845 |
| Segment à fort taux d’alertes, tickets à +3 mois | r = **+0,242** : sens opposé à une alerte de baisse | 188 observations, 71 magasins, 16 mois |
| Même segment, CA à +3 mois | r = +0,211 | 188 observations, 71 magasins, 16 mois |
| NPS | Historique insuffisant pour conclure | Au plus 3 périodes utilisables ; 2 en intra-magasin |

Les plages couvrent les trois horizons et les trois indicateurs commerciaux. Les effectifs exacts par test figurent dans `resultats.csv`. Les coefficients sont descriptifs : observations répétées par magasin, tests multiples, aucune significativité ou causalité revendiquée. Un coefficient plus élevé dans un segment ne démontre pas une différence statistique entre segments.

**Traitement essentiel :**

- Alertes négatives / tickets × 10 000 ; 2 503 valeurs manquantes conservées comme manquantes, pas comme zéros.
- Une observation à la fin de chaque vague de 2 mois et de chaque semestre NPS. Juillet–octobre 2026 constitue une période NPS distincte ; sans mois futur disponible, elle ne contribue pas aux tests.
- Croissance commerciale annuelle ; octobre 2026 exclu des résultats commerciaux car arrêté au 26 inclus.
- Intra-magasin : variation de satisfaction depuis la période précédente → variation ultérieure de croissance annuelle ; retrait des effets fixes magasin et mois calendaire. Seuls les magasins avec au moins deux observations complètes contribuent.
- Segments : quartile supérieur du taux d’alertes ou quartile inférieur du score, calculé séparément à chaque période, sans données futures.
- Doublons 123 en mai–juin 2026 : valeurs communes conservées, scores contradictoires mis à manquant.
- Seuil indicatif d’insuffisance : moins de 30 observations, 10 magasins ou 3 périodes ; pour le NPS, moins de 6 périodes.

**Limite temporelle :** disponibilité des scores supposée en fin de période. Sans dates réelles de publication, l’absence de fuite temporelle ne peut pas être certifiée. Aucun score n’est utilisé au début de sa période de collecte.

**Action :** utiliser les thèmes/verbatims pour cibler les investigations métier. Ne pas présenter ces corrélations comme un système d’alerte précoce validé.

## Réutilisation

```python
from scripts.analyser_decalages import analyser
resultats = analyser(final_df)
```

Le code sélectionne les colonnes utiles du DataFrame Spark puis les convertit en pandas pour cette analyse compacte (3 591 lignes dans l’export). À réserver à un volume tenant en mémoire du pilote. `customer_count` n’est jamais utilisé comme fréquentation.
