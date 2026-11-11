import json,re,unicodedata,collections,pathlib,openpyxl
P=pathlib.Path(__file__).parent
def norm(t):
 t=unicodedata.normalize('NFKD',str(t or '').lower().replace('’',"'"))
 return ''.join(c for c in t if not unicodedata.combining(c))
def rx(p):return re.compile(p,re.I)
THEMES={
 'Prix et rapport qualité/prix':r'\bprix\b|\bcher\w*|\bchere\w*|tarif|rapport qualite|cout\b|pouvoir d.achat|abordable|ارخص|اثمنة|اسعار|الثمن|غالي|غلاء|غلا|غالية',
 'Affichage et exactitude des prix':r'etiquet|balisage|affich|prix.{0,40}(?:caisse|rayon)|(?:caisse|rayon).{0,40}prix|difference.{0,20}prix|prix.{0,20}difference|borne.{0,20}(?:prix|lecture)|code.?barre|الثمن.{0,20}(?:مكتوب|واضح)|الاثمنة.{0,20}(?:مكتوب|واضح)',
 'Promotions':r'promo|depliant|catalogue|offre[s]?\b|reduction|remise|soldes|تخفيض|عروض',
 'Disponibilité et choix des produits':r'rupture|disponibilite.{0,20}(?:produit|article)|(?:produit|article).{0,20}disponib|(?:manque|manquent|manquer|absence|absen|trouv|cherche|ajout|approvision|assortiment|variet|choix).{0,55}(?:produit|article|marque|rayon|stock|fromage|lait|pain|poisson|fruit|legume)|(?:produit|article|marque|rayon|stock).{0,55}(?:manque|manquent|absen|trouv|choix|variet|disponib)|reassort|reapprovision|stock|اختيار|تنوع|متوفر|متوفرة|المواد.{0,25}كيساليو',
 'Qualité et fraîcheur des produits':r'perim|perempt|avari|fraich|fraic[h]?eur|moisi|moisiss|pourri|pourrit|chaine du froid|date.{0,20}(?:limite|expir|consomm)|qualite.{0,25}(?:produit|fruit|legume|viande|poisson|pain|article)|(?:produit|fruit|legume|viande|poisson|pain|article).{0,25}qualite|intoxic|insect|cafard|mouche|gout|bouchonne|immange|im[b]?uvable|odeur|mauvaise viande|منتوج.{0,20}جود|جودة|فاسد|صلاحية|متعفن|بارد',
 'Propreté et hygiène':r'propret|hygien|\bsale[s]?\b|salete|nettoy|toilette|sanitaire|dechet|poubelle|cafard|mouche|rat[s]?\b|نظاف|وسخ|نظيف|متسخ',
 'Accueil et comportement du personnel':r'accueil|accueill|amabil|aimable|souri|souria|politesse|impoli|courtoi|respect|attitude|comportement|arrog|agress|insult|gentil|serviab|sympath|desagreable|agreable.{0,20}(?:personnel|equipe)|racis|discrimin|professionn|personnel|caissier|caissiere|employe|responsable|gerant|equipe|collaborat|عامل|عمال|موظف|مستخدم|معامل|اخلاق|استقبال',
 'Disponibilité et compétence du personnel':r'(?:manque|absen|disponib|trouv|cherch|qualifi|compet|formation).{0,40}(?:personnel|employe|vendeur|collabor|responsable)|(?:personnel|employe|vendeur|collabor|responsable).{0,40}(?:manque|absen|disponib|trouv|qualifi|compet)|personne.{0,25}(?:rayon|peser|servir)|manque de professionn|خدمة|المستخدمين',
 'Attente et ouverture des caisses':r'attente|attend|attendre|queue|\bfile\b|caisses?.{0,35}(?:ouvr|ouvert|ferm|unique|seule|nombre|insuff)|(?:ouvr|ouvert|ferm|unique|seule|nombre|plus de|manque de|pas assez).{0,35}caiss|rapidite|lent[eus]|20 min|30 min|15 min|heure.{0,12}caisse|انتظار|الصناديق|صندوق',
 'Paiement, monnaie et facturation':r'paiement|payer|paye|monnaie|centime|factur|ticket|encaisse|debit|tpe\b|carte bancaire|carte.{0,15}(?:banc|paiement)|double.{0,15}(?:compte|prix|achat)|دفع|صرف|الباقي',
 'Fidélité et application':r'fidelit|carte client|bon[s]? d.achat|cagnott|application|\bappli\b|points|compte client|\bapp\b|نقاط|وفاء|تطبيق',
 'Réclamations, retours et remboursement':r'rembours|service apres.vente|\bsav\b|retour.{0,20}(?:produit|article)|echang.{0,20}(?:produit|article)|reclamation.{0,30}(?:reponse|suite|traite)|(?:repond|reponse).{0,30}reclamation|تعويض|استرجاع',
 'Confort, circulation et équipements':r'chariot|caddie|panier|climat|clim\b|chaleur|chaud|temperature|froid.{0,15}magasin|encombr|circul|rangement|range\b|organis|desordre|musique|bruit|eclair|lumiere|wifi|wi.fi|reseau|balance|agenc|espace|ascenseur|escal|عربة|عربات|كروسة|كروسات|تنظيم|تكييف|حرارة',
 'Parking et accès':r'parking|stationn|acces|accessib|emplacement|proximite|localisation|proche|باركينغ|موقف',
 'Sécurité':r'securite|vigile|gardien|fouille|vol\b|voleur|harcel|حارس|حراس|امن|سرقة',
 'Horaires':r'horaire|ouverture|fermeture|ferme.{0,12}(?:heure|tot)|ouvre.{0,12}(?:heure|tard)|توقيت|اغلاق',
 'Livraison et commandes':r'livrais|livreur|commande|glovo|jumia|توصيل|طلبية',
 'Services en magasin':r'apres.caiss|emball|sachet|sac[s]?\b|pes[eé]|peser|decoupe|stand coupe|boucher|fromager|charcut|boulanger|poissonner|بعد الصندوق|اكياس',
}
THEMES={k:rx(v) for k,v in THEMES.items()}
EXTRA={
 'Prix et rapport qualité/prix':r'overpriced|expensive|تمن|اثمنة|اتمنة',
 'Disponibilité et choix des produits':r'produits?.{0,25}(?:n.existe|inexistan|retire|nn dispo)|(?:rayon|fromage|produit).{0,25}vide|choix|diversifi|gamme|references|ramenez|retour du pain|rayons?.{0,20}khaw|منتوج|منتجات|حاجات|سلع',
 'Qualité et fraîcheur des produits':r'expir|dlc|oxyd|grumeau|caille|decongel|recongel|fondu|acidule|insect|خامج|خانز|حشرات|نتنة|dode|khamej|damaged|fresh products|laitier|qualite des|qualite.*viande',
 'Accueil et comportement du personnel':r'acceuil|aceul|accueu|vulgair|insolen|incompet|caussi|staf[f]?|customer|staff|cashier|ta3amol|معاملة|تعامل|سكيرتي',
 'Disponibilité et compétence du personnel':r'personne.{0,25}(?:fromager|boucher)|(?:fromager|boucher).{0,25}(?:vide|vacant|personne)|effectif|competence|incompet|recrut|embauch|former|formation|formez',
 'Attente et ouverture des caisses':r'self.checkout|cash registers|checkout|\bwait|(?:une|un|deux|2|seule|seul|peu de|plus de|manque de).{0,18}caiss|caiss.{0,20}(?:limite|pleine|pliene|point noir)|min d.attente|لاكيس|لكيص|لاكيز|كشك',
 'Paiement, monnaie et facturation':r'(?:factur|saisi|compte|charg|paye).{0,25}(?:deux|2) fois|recu|الفاتورة|الفاكتورا',
 'Fidélité et application':r'bonus|النقط|نقط|بطاقة|بطاق|notes',
 'Réclamations, retours et remboursement':r'(?:reclamation|reclamations|demande|question).{0,60}(?:reponse|repond|suite)|(?:aucune?|pas de|attend|attente).{0,25}reponse|شكاية|شكايتي',
 'Confort, circulation et équipements':r'(?:magasin|espace|surface).{0,20}(?:petit|reduits|etroi)|tapis|palett|allees|retrec|messy|disorganised|air condition|حرارة|تنظيم',
 'Services en magasin':r'cafeteria|cafe\b|restaur|مقهي|مطعم|اكياس',
}
for k,v in EXTRA.items():THEMES[k]=rx(THEMES[k].pattern+'|'+v)
THEMES['Disponibilité et choix des produits']=rx(THEMES['Disponibilité et choix des produits'].pattern.replace('|trouv','')+r'|(?:trouve pas|ne trouve|plus trouver|jamais trouv|introuvable).{0,35}(?:produit|article|marque|fromage|pain|lait|rayon)')
POS=rx(r'\b(?:excellent\w*|parfait\w*|super|top|bravo|satisfait\w*|satisfaction|formidable|impeccable|magnifique|agreable\w*|aimable\w*|gentil\w*|serviable\w*|sympath\w*|courtois\w*|professionnel\w*|souriant\w*|propre\w*|rapide\w*|efficace\w*|abordable\w*|raisonnable\w*|ador\w*|recommand\w*|appreci\w*|felicit\w*)\b|tres bien|tout.{0,8}bien|bonne continuation|bon courage|bon accueil|bien accueilli|bien servi|bon service|bonne qualite|bon rapport|bon magasin|bon personnel|bonne equipe|rien a (?:dire|signaler|reprocher)|pas de (?:probleme|souci)|a l.ecoute|thank you|very good|\bgood\b|\bnice\b|\bgreat\b|ممتاز|رائع|جيد|مزيان|زوين|شكرا|برافو|👍|❤️|❤|😍|👏|🙏|😊')
NEG=rx(r'\b(?:probleme\w*|mauvais\w*|mal\b|mediocre\w*|nul\w*|catastroph\w*|horrible\w*|decu\w*|decev\w*|deception|insatisf\w*|mecontent\w*|inadmissible|inacceptable|scandale\w*|honte\w*|dommage|regrett\w*|malheureus\w*|abus\w*|arnaqu\w*|vol\w*|trich\w*|cher\w*|eleve\w*|excessif\w*|exagere\w*|manque\w*|manquant\w*|rupture\w*|indisponib\w*|absen\w*|insuffisan\w*|erreur\w*|errone\w*|difference\w*|different\w*|incorrect\w*|faux|fausse\w*|lent\w*|longue\w*|impoli\w*|irrespect\w*|desagreable\w*|arrog\w*|agress\w*|insult\w*|refus\w*|sale\w*|salete|perim\w*|avari\w*|moisi\w*|pourri\w*|intoxi\w*|cafard\w*|mouche\w*|odeur\w*|bouchonne\w*|im[b]?uvable|encombr\w*|desordre|difficil\w*|impossible|degrad\w*|defect\w*|panne\w*|casse\w*|abime\w*)\b|pas.{0,20}(?:affich|disponib|trouv|respect|propre|aimable|professionnel|satisfait|correct|normal|bon|frais|marche|fonction)|ne.{0,25}(?:pas|jamais|plus)|sans.{0,15}(?:prix|etiquette|respect|sourire)|trop (?:de|d.|peu|chaud|froid|bruit)|pas assez|laisse.{0,15}desirer|faire la queue|attendre.{0,15}(?:min|heure)|plus de caiss|ouvrir.{0,15}caiss|\bbad\b|\brude\b|poor|expensive|dirty|سيء|سيئ|غالي|غلاء|غلا|غير متوفر|ليس|ما كاين|ماكين|مكاين|مشك|نقص|فاسد|وسخ|متسخ|تنتظر|طويل|عدم|لا يوجد|لا توجد|لا يحترم|خايب|😡|😠|👎')
SUG=rx(r'amelior|devrai|faudrai|souhait|sugg|propos|besoin|plus de|davantage|augment|redui|baisser|veille|revoir|merci de|priere|pourriez|pensez|j.aimerais|نتمنى|يجب|خاص|خص|بغيت')
POS=rx(POS.pattern.replace('propre\\w*','propres?').replace('rapide\\w*','rapides?')+r'|\bcontent[e]?\b|\bsympa\b|\bsuperbe|\bmeilleur|\bmerveille|\bfiable|bien gere|bien entretenu|bon travail|bon job|bon continuation|bonne chance|bon chance|bons services|encouragement|\bj.aime\b|vous aime|\bjoli|reactivite|\bcompliment|felicitation|felecitation|gratulation|remerciement|continuez|continuer ainsi|\bc.est bon\b|\bc bon\b|\bc bien\b|\btoop\b|\bnadi\b|zwiin|zwin|satisfi\b|\bsatisfaisant|🥰|☺|🤗')
NEG=rx(NEG.pattern+r'|desolant|retard|peux mieux faire|peut mieux faire|faible|incompet|insolen|vulgair|irresponsab|deplor|lamentab|pire|penurie|expir|dlc depasse|oxyd|grumeau|caille|decongel|recongel|fondu|acidule|insect|sans gants|sans des gants|trop long|interminable|trop petit|trop fort|trop reduit|peu de|rarement|pas (?:toujours|logique|identique|suffisamment|a la hauteur)|pas.{0,20}meme|plus cher|prix.{0,20}(?:augment|plus que)|autre prix|discord|decalage|ecart|incompatible|inexistan|non disponibil|non mis a jour|non pris en compte|non compt|non profession|non qualif|deux fois|2 fois|en vain|aucune? (?:reponse|solution|employe|personnel)|personne.{0,15}(?:repon|present)|regulierement.{0,20}prix|supprim|diminu|retire|perdu|perte|finit son|arrete avant|avant l.heure|sinon rien|ne gagne rien|en colere|derang|penible|frustr|boycott|maltrait|agression|danger|accident|blesse|douleur|crie|crit que|ignor|fout|marre|gaspille|nuisance|pas servi|sans clim|quality zero|qualite zero|unpleasant|unacceptable|worse|damaged|overpriced|lack|messy|disorganised|cockroach|empty|closed|long time|couldn.t|ignored|خايب|خانز|نتنة|حشرات|منتهي|مرتفعة|مرتفع|ارتفاع|زيادة|طالعة|غير مقبول|غير لائق|بطء|بطي|تأخير|غياب|سيئة|سيء|نفس المشكل|مختلف|مغاير|تلاعب|دون المستوى|مكايبغيوش|khameje|khawyin|makinch|makhdithomch|t9il|mouvais')
def sentiment(t):
 t=norm(t)
 # Courtesy in a request is not positive feedback.
 t=re.sub(r'merci(?: beaucoup)?(?: de| pour votre (?:attention|comprehension|retour)).*?(?=[.!?\n]|$)',' ',t)
 t=re.sub(r'je vous remercie (?:par avance|d.avance|pour votre attention).*?(?=[.!?\n]|$)',' ',t)
 t=re.sub(r'bonne (?:journee|soiree)',' ',t)
 t=re.sub(r'\bsuper[ -]?marche|\bpropre[s]? (?:argent|compte|mot|mots|employe|yeux|telephone)|parfaitement|\bcher (?:responsable|monsieur|madame)|excellente journee|vous savez tres bien|ni de remerciements|ni remerciements',' ',t)
 if NEG.search(t):t=re.sub(r'bonne continuation|bon courage|bonne chance|bon continuation',' ',t)
 # Suppress positive words under negation, unmet expectations, and desired future service.
 t=re.sub(r'(?:pas|non|peu|manque de|manquent de|sans|aucun\w*|loin d.etre|au lieu d.etre|devrait etre|doit etre|etre plus|doivent etre)\s+(?:du tout\s+|tres\s+|assez\s+|trop\s+)?(?:satisfait\w*|satisfaction|aimable\w*|agreable\w*|professionnel\w*|courtois\w*|respect\w*|propre\w*|souriant\w*|gentil\w*|efficace\w*|rapide\w*|bon\w*|sympath\w*|compliment\w*|apprecie\w*)',' negatif ',t)
 t=re.sub(r'recommande\w* pas',' negatif ',t)
 t=re.sub(r'(?:pas de|aucun) (?:probleme|souci)|rien a (?:dire|signaler|reprocher)',' positif ',t)
 n=bool(NEG.search(t) or ' negatif ' in t)
 positive_text=re.sub(r'(?:il faut|il faudrait|j.attends|je m.attend|j.esper|devrait|devraient|doivent|veuillez|merci de|souhaite|attendu|veillent|je demande|au lieu de|dans l.attente|pour ameliorer|afin d. ameliorer|pour offrir|pour assurer|doit etre)[^.!?\n]*',' ',t)
 p=bool(POS.search(positive_text) or ' positif ' in t)
 if not n and re.search(r'\bmerci\b',t) and not SUG.search(t) and not re.search(r'\?|comment|pourquoi|quand|combien',t):p=True
 if p and n:return 'Mixte'
 if n:return 'Négatif'
 if p:return 'Positif'
 if re.fullmatch(r'\s*(?:merci\w*|bien|ok|oui|ras|r\.a\.s\.?|tb|satisfaisant|parfaite?|tres bon|bon|bonne|nic|nice)[\s!.]*',t):return 'Positif'
 return 'Neutre'
def analyze(text):
 t=norm(text).strip()
 if not t:return 'Non analysable',[('Absence de verbatim','Non analysable')]
 if not re.search(r'[a-z\u0600-\u06ff👍❤😍👏🙏😊😡😠👎]',t):return 'Non analysable',[('Contenu non interprétable','Non analysable')]
 clauses=[x.strip() for x in re.split(r'[.!?;\n]+|\bmais\b|\bcependant\b|\bpar contre\b|\ben revanche\b',t) if x.strip()]
 overall=sentiment(t)
 found=collections.defaultdict(list)
 for clause in clauses:
  for theme,p in THEMES.items():
   if p.search(clause):found[theme].append(clause)
 # General price mentions in pricing-label complaints are not an affordability judgement.
 if 'Affichage et exactitude des prix' in found and not rx(r'cher\w*|eleve\w*|abordable|raisonnable|rapport qualite|cout|redui|baisser|prix.{0,12}(?:haut|bas|bon)|غالي|غلاء').search(t):found.pop('Prix et rapport qualité/prix',None)
 if 'Accueil et comportement du personnel' in found and 'Disponibilité et compétence du personnel' in found and not rx(r'accueil|politesse|impoli|courtoi|respect|attitude|comportement|arrog|agress|insult|gentil|serviab|sympath|desagreable|aimable|souri|racis|discrimin').search(t):found.pop('Accueil et comportement du personnel',None)
 if 'Accueil et comportement du personnel' in found and len(found)>1 and not rx(r'accueil|accueill|politesse|impoli|courtoi|respect|attitude|comportement|arrog|agress|insult|gentil|serviab|sympath|desagreable|aimable|souri|racis|discrimin|profession|compet|vulgair|insolent|nul|mediocre|mauvais|service|thank|merci.{0,15}(?:equipe|personnel)|نظ|معامل|تعامل').search(t):found.pop('Accueil et comportement du personnel',None)
 if not found:
  if overall=='Neutre' and (len(t)<35 or re.search(r'\b(?:adresse|rue|avenue|quartier|cv|emploi|stage|recrut|candidature)\b',t)) and not SUG.search(t):return 'Non analysable',[('Contenu non interprétable / hors sujet','Non analysable')]
  return overall,[('Expérience globale',overall)]
 pairs=[]
 for theme,cs in found.items():
  s=sentiment(' . '.join(cs))
  if s=='Neutre' and overall in ['Négatif','Positif']:s=overall
  pairs.append((theme,s))
 return overall,pairs
if __name__=='__main__':
 ids={str(r[3]).strip() for r in list(openpyxl.load_workbook('nps.xlsx',read_only=True,data_only=True)['MARKET'].values)[1:] if r[3]}
 raw=json.loads((P/'market.json').read_text(encoding='utf-8'))
 overrides=json.loads((P/'overrides.json').read_text(encoding='utf-8')) if (P/'overrides.json').exists() else {}
 out=[]
 for i,r in enumerate(raw):
  if str(r['ID PDV']) not in ids:continue
  s,ts=analyze(r['Verbatim'])
  if str(i) in overrides:s,ts=overrides[str(i)]
  out.append({'i':i,'source':r,'overall':s,'themes':ts,'reviewed':str(i) in overrides})
 (P/'classified.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8')
 print('alerts',len(out),'theme rows',sum(len(x['themes']) for x in out),'sentiments',collections.Counter(x['overall'] for x in out),'reviewed',sum(x['reviewed'] for x in out))
 print('themes',collections.Counter(t for x in out for t,s in x['themes']))
