// Test fonctionnel du rendu et des changements de sélection, sans navigateur.
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const path=require('node:path');
const base=path.resolve(__dirname,'../outputs/analyse_market');
const code=fs.readFileSync(path.join(base,'verification_interface.js'),'utf8');
const donnees=fs.readFileSync(path.join(base,'donnees_tableau_de_bord.json'),'utf8');
const elements={};
for(const id of ['source','periode','seuil','seuil-valeur','bilan','lignes','page','precedent','suivant','magasin','detail','signal','test']){
  elements['am-'+id]={value:'',innerHTML:'',textContent:'',disabled:false,evenements:{},addEventListener(type,fn){this.evenements[type]=fn;}};
}
const contexte={Intl,console,document:{getElementById(id){if(id==='analyse-market')return {querySelector:s=>elements[s.slice(1)]};if(id==='am-donnees')return {textContent:donnees};throw Error('Élément inconnu : '+id);}},window:{addEventListener(){}}};
vm.runInNewContext(code,contexte);
assert.match(elements['am-bilan'].textContent,/111 magasins · 109 comparables · 29 baisses/);
assert.match(elements['am-detail'].innerHTML,/Ouled Salah/);
assert.match(elements['am-detail'].innerHTML,/r43jJZKOnd/);
elements['am-seuil'].value='25';elements['am-seuil'].evenements.input();
const sensibilite=JSON.parse(donnees).sensibilite.find(x=>x.seuil_baisse_points===25);
assert.match(elements['am-bilan'].textContent,new RegExp(sensibilite.baisses_score+' baisses'));
elements['am-source'].value='NPS';elements['am-source'].evenements.change();
assert.equal(elements['am-periode'].value,'2026-06-30');
elements['am-periode'].value='2026-10-23';elements['am-periode'].evenements.change();
assert.match(elements['am-bilan'].textContent,/0 comparables · 0 baisses/);
assert.match(elements['am-signal'].innerHTML,/YAACOUB MANSOUR/);
assert.match(elements['am-test'].innerHTML,/583/);
const verification=JSON.parse(fs.readFileSync(path.join(base,'verification_regles.json'),'utf8'));
verification.interface={statut:'Tests fonctionnels réussis',controles:['Rendu initial et commentaire associé','Changement de seuil et recomptage','Passage au NPS et sélection de période','Exclusion de la période partielle','Affichage des signaux et du bilan'],controle_visuel:'Non réalisé : aperçu navigateur local inaccessible (délai de connexion dépassé)'};
fs.writeFileSync(path.join(base,'verification_regles.json'),JSON.stringify(verification,null,2));
console.log('Tests fonctionnels du tableau de bord réussis.');
