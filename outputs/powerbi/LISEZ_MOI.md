# Page Power BI — vue mensuelle par magasin

Ouvrir `dash-bnps.pbip` à la racine du projet. La page utilise uniquement des visuels natifs Power BI, sans barre de navigation latérale. Sélection initiale : Ouled Salah (742), août 2026.

## Lecture

- Les segments **Magasin** et **Mois** sélectionnent un seul magasin et un seul mois.
- Le **NPS** est celui de la période source contenant le mois. Son libellé et le nombre de répondants sont affichés dessous. S2 2026 correspond à l'extraction arrêtée au 23 octobre ; ce n'est pas un semestre complet ni un NPS mensuel.
- Le **Baromètre** est le score global de la vague contenant le mois, sur l'échelle originale −600 à +300. Une vague absente donne une valeur vide, sans report de la dernière vague.
- CA, fréquentation et panier sont mensuels. Fréquentation = tickets ; panier = CA / tickets. La devise n'étant pas spécifiée dans le fichier source, aucun symbole monétaire n'est ajouté.
- Les deux courbes présentent les douze mois jusqu'au mois choisi, avec une série N-1. Les variations sous les cartes comparent le mois au même mois de l'année précédente.
- Octobre 2026 : CA et tickets jusqu'au 26 inclus ; NPS et alertes jusqu'au 23. Les comparaisons annuelles commerciales sont absentes pour ce mois partiel.
- Les thèmes et verbatims sont strictement limités au mois sélectionné. Les commentaires sont triés par date décroissante ; le tableau reste défilable pour consulter les autres commentaires du mois.

## Couleurs des thèmes

La part négative est le nombre de commentaires négatifs du thème divisé par le nombre de commentaires analysables du magasin sur le mois. Un commentaire peut mentionner plusieurs thèmes.

| Niveau | Règle | Couleur |
|---|---|---|
| Aucune mention négative | 0 | Gris |
| Isolé | 1–2 mentions négatives | Jaune clair |
| Récurrent | Au moins 3, part inférieure à 50 % | Orange |
| Prioritaire | Au moins 3, part d'au moins 50 % | Rouge |

Ce sont des niveaux de tri pour investigation, pas une gravité métier validée ni une prédiction. La classification des commentaires reste exploratoire.

## Modèle et maintenance

Cinq tables importées : Magasins, Periodes, Mensuel, Themes, Verbatims. Magasins filtre les trois tables de faits par le code. Periodes est volontairement déconnectée : les mesures appliquent le mois aux indicateurs et aux thèmes, tout en conservant douze mois sur les courbes.

Les CSV de ce dossier alimentent les partitions Power Query. Leurs chemins sont absolus ; adapter `File.Contents` dans les partitions si le projet change d'emplacement. Le script `scripts/construire_powerbi.py` régénère les CSV, les mesures et les visuels à partir des données préparées. Il remplace les éléments générés ; ne pas le relancer après une personnalisation manuelle sans sauvegarde.

Une sauvegarde du projet vierge est conservée dans `.work_powerbi/sauvegarde_initiale`. Les fichiers de visuels et de page ont été contrôlés avec les [schémas PBIR officiels Microsoft](https://learn.microsoft.com/power-bi/developer/projects/projects-report).

## Indicateur de verbatims et habillage

La sixième carte affiche la part de verbatims globalement négatifs parmi les commentaires analysables du magasin et du mois sélectionnés. Le sous-titre affiche les effectifs négatifs/analysables et le nombre total de commentaires non vides. Les sentiments mixtes ne sont pas comptés comme négatifs. Sans commentaire analysable, le pourcentage reste vide. Il s'agit des alertes enregistrées, pas d'un taux d'insatisfaction de l'ensemble des clients.

Le logo Carrefour Market fourni est incorporé au projet, sans modification. Les titres des indicateurs et des tableaux comportent des pictogrammes. Pour réappliquer ces ajouts après une reconstruction complète, utiliser `scripts/enrichir_powerbi.py` ; la copie source du logo se trouve également dans `dash-bnps.Report/StaticResources/RegisteredResources/carrefour-market.png`.

## Vérification effectuée dans Power BI Desktop

Le projet a été ouvert, actualisé et enregistré dans Desktop. Une erreur transitoire de référence cyclique au premier chargement a disparu à la seconde actualisation, sans changement des requêtes.

Valeurs contrôlées pour Ouled Salah en août 2026 : NPS 31, score global 223,4, CA 2 505 649, 27 179 tickets et panier 92,19. Le passage à octobre a été testé : mise à jour des courbes, thèmes et verbatims, absence de score Baromètre et de comparaison annuelle commerciale, affichage des dates de coupure. Les couleurs conditionnelles et le retour à août ont été vérifiés visuellement. Le projet est enregistré sur la vue d’août.
