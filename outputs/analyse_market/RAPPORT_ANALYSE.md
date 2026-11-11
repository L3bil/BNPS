# Market — première analyse métier

## Ce qui répond à l’objectif

L’analyse croise maintenant la satisfaction avec les performances commerciales, identifie les magasins à examiner, rapproche leurs scores détaillés des commentaires de la même période et recherche des hausses récentes de thèmes négatifs. Un premier test historique vérifie si une règle de divergence précède une baisse de fréquentation.

Le résultat est un POC exploratoire : les écarts et les commentaires sont exploitables pour une revue métier ; la capacité à anticiper une anomalie commerciale n’est pas démontrée.

## 1. Où satisfaction et performance divergent-elles ?

Dernière vague Baromètre : **juillet–août 2026**, 111 magasins, dont 109 avec une variation comparable. **29 magasins perdent au moins 15 points** par rapport à mai–juin.

| Catégorie exclusive | Magasins |
|---|---:|
| Baisse de satisfaction et baisse de fréquentation d’au moins 5 % | 5 |
| Baisse de satisfaction, CA stable ou en hausse, hors catégorie précédente | 19 |
| Autres baisses de satisfaction d’au moins 15 points | 5 |
| Sans déclenchement | 80 |
| Comparaison insuffisante | 2 |

La variation de satisfaction compare deux vagues consécutives. Les variations du CA, des tickets et du panier comparent la période à la même période de l’année précédente. Ces horizons différents sont conservés et affichés : ce rapprochement repère un décalage, il ne mesure pas une causalité.

### Cas concrets à examiner

| Magasin | Variation du score global | CA annuel | Tickets annuels | Première piste |
|---|---:|---:|---:|---|
| Ouled Salah — 742 | −44,08 points | +45,17 % | +29,71 % | Exactitude des prix et fraîcheur |
| Bellerive — 179 | −36,41 points | +1,55 % | +4,96 % | Disponibilité des promotions et exactitude des prix |
| Fes Immouzzer — 117 | −36,19 points | +9,22 % | +11,82 % | Prix du poisson et attente en caisse |
| Kamal Parc — 198 | −32,96 points | −9,42 % | −8,01 % | Prix et qualité des produits frais |
| Khemissat — 119 | −22,47 points | −10,30 % | −5,91 % | Dégradation commerciale déjà observable |

Les cinq dégradations conjointes concernent **Khemissat, Ouarzazate, Kamal Parc, Océan et Othmane Ibnou Affane**. Elles nécessitent une investigation opérationnelle immédiate, sans attendre une prédiction.

Jnan Gueliz — 7107 présente également une forte baisse du score (−53,98 points) malgré un CA en hausse. Son identifiant n’appartient pas au périmètre des verbatims Market retenu à partir du NPS : aucun commentaire ne lui est attribué dans cette analyse.

## 2. Qu’est-ce qui permet d’expliquer les écarts ?

**Exemple : Ouled Salah, juillet–août 2026.** Le score global baisse de 44,08 points alors que le CA progresse de 45,17 %.

- L’exactitude des prix entre rayon et caisse baisse de **122,22 points**. Deux alertes de la même période comportent une mention négative de ce thème.
- La qualité/fraîcheur des produits frais traditionnels baisse de **100 points**. Une alerte concerne le thème plus large de la qualité et de la fraîcheur ; elle ne porte pas nécessairement sur ce rayon précis.
- Le rapport qualité/prix baisse de **95,43 points**, sans mention négative associée à ce thème dans les alertes disponibles pour cette période.

L’alerte `r43jJZKOnd` du 12 août mentionne : « Les prix affichés ne sont pas sur la facture, et ce n est pas la première fois c est repetitif, il faut toujours faire attention et vérifier la facture ».

**Action proposée :** contrôler un échantillon de prix rayon/caisse, vérifier les changements d’étiquettes et les promotions, puis documenter le résultat dans la grille de revue métier. Le rapprochement entre baisse du score et commentaire donne une piste concrète à vérifier ; il ne prouve pas que ce problème explique toute la baisse du score global.

Les scores détaillés ne sont donc pas supprimés. Ils servent à orienter l’investigation. Sans pondération connue du score global, leurs variations ne sont pas présentées comme des contributions mathématiques à ce score.

## 3. Quel signal récent ressort des commentaires ?

Dernière évaluation hebdomadaire complète : **18 octobre 2026**, avec des commentaires disponibles jusqu’au 23 octobre.

**Yaacoub Mansour — 143 : affichage et exactitude des prix.**

- Du 21 septembre au 18 octobre : **3 mentions négatives sur 6 commentaires analysables**, soit 50 %.
- Du 27 juillet au 20 septembre : **3 sur 17**, soit 17,65 %.
- La part augmente de **32,35 points**, avec une fréquence relative multipliée par 2,83.
- Exemple : « La majorité des produits n’ont pas le bon prix affiché ».

**Action proposée :** vérifier les trois alertes et effectuer un contrôle des prix affichés. Le volume reste faible : c’est un signal à examiner, pas une anomalie confirmée. Il décrit exclusivement les alertes enregistrées.

## 4. Règles testables

| Règle | Conditions initiales |
|---|---|
| Baisse Baromètre | Perte d’au moins 15 points entre deux vagues consécutives |
| Baisse NPS | Perte d’au moins 10 points, avec au moins 30 réponses dans chacune des deux périodes ; dernière période partielle exclue du classement |
| Dégradation conjointe | Baisse de satisfaction et tickets en baisse d’au moins 5 % sur un an |
| Divergence | Baisse de satisfaction et CA stable ou en hausse sur un an |
| Hausse d’un thème négatif | Fenêtre récente de 28 jours contre les 56 jours précédents ; au moins 5 et 10 commentaires analysables respectivement ; au moins 3 mentions négatives récentes ; hausse de part d’au moins 15 points et part au moins doublée |

Pour le classement exclusif, la dégradation conjointe prend priorité sur la divergence. Les seuils sont des hypothèses de travail. Le tableau de bord permet d’explorer le seuil de baisse du score ; le test historique présenté reste celui du seuil initial de 15 points.

Les fenêtres de commentaires utilisent des nombres de commentaires analysables, pas le nombre de clients ni le nombre de tickets. Un commentaire peut mentionner plusieurs thèmes ; les parts par thème ne s’additionnent donc pas à 100 %.

## 5. Le signal permet-il déjà d’anticiper ?

**Pas avec la règle testée.** Le test regarde si une baisse du Baromètre d’au moins 15 points, accompagnée d’un CA stable ou en hausse, précède une baisse des tickets d’au moins 5 % à la vague suivante. Les magasins déjà en baisse de tickets d’au moins 5 % sont exclus de ce test.

| Groupe historique | Observations magasin × vague | Baisse future des tickets | Taux |
|---|---:|---:|---:|
| Avec signal de divergence | 100 | 7 | 7,00 % |
| Sans signal de divergence | 583 | 52 | 8,92 % |

La règle ne montre donc **aucun gain prédictif dans cette comparaison descriptive**. Les observations répétées d’un magasin ne sont pas indépendantes ; ce résultat n’est pas une estimation validée de performance d’un modèle. Les dates de publication du Baromètre manquent également pour simuler précisément ce qui aurait été connu au moment d’une décision.

Pour les thèmes, 82 déclenchements hebdomadaires correspondent à 39 épisodes espacés d’au moins 28 jours pour un même magasin/thème. Parmi les 31 épisodes ayant une fenêtre future complète et au moins 5 commentaires analysables, **5 satisfont le critère de persistance** : au moins 3 mentions négatives dans les 28 jours suivants et une part dépassant d’au moins 10 points la référence initiale. Ce ratio mesure une persistance selon cette règle, pas une précision de détection métier.

## 6. Livrables et validation métier

- `ecarts_satisfaction_performance.csv` : historique rapproché, catégories et comparaisons.
- `baisses_indicateurs_derniere_vague.csv` : baisse des scores détaillés, sans suppression des dimensions.
- `verbatims_appui.csv` : extraits, dates et identifiants des alertes pour retrouver les preuves.
- `signaux_themes_derniere_evaluation.csv` et `signaux_themes_historique.csv` : signaux récents et historiques.
- `test_chronologique_divergences.csv`, `bilan_test_chronologique.csv` et `episodes_themes_suivi.csv` : détail des tests.
- `sensibilite_seuils.csv` : nombre de cas selon quatre seuils Baromètre.
- `revue_metier.csv` : 20 baisses importantes et le signal thématique récent à qualifier pendant la semaine de test. Les autres baisses restent accessibles dans le tableau de bord et le fichier complet des écarts.

Pendant la semaine de test, le métier indique pour chaque cas si le signal est confirmé, l’action décidée, le responsable et la date de revue. Ces retours permettront de choisir les seuils utiles et de mesurer le volume de fausses alertes métier.

## 7. Limites à prendre en compte avant industrialisation

- Les comparaisons commerciales du NPS partiel juillet–23 octobre restent indisponibles : les transactions d’octobre vont jusqu’au **26 inclus**. Aucune extrapolation n’est utilisée.
- Les effectifs de répondants du Baromètre manquent : les écarts de scores ne sont pas des tests de significativité.
- Les sentiments et thèmes proviennent d’une classification lexicale/contextuelle avec revue ciblée. Leur qualité n’a pas été mesurée sur un échantillon annoté indépendamment. Les alertes prioritaires doivent être relues.
- Les correspondances entre indicateurs détaillés et thèmes sont des associations de travail à valider.
- Les commentaires servent à examiner les problèmes effectivement mentionnés dans les alertes disponibles.

**Prochaine étape :** valider les cas et la qualité des thèmes avec le métier, ajuster les règles, puis évaluer d’autres signaux sur une période ultérieure réservée. L’industrialisation et une promesse de prédiction exigent cette validation.
