import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const req=createRequire('C:/Users/abdellah.ngar/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const root='C:/Users/abdellah.ngar/Desktop/BNPS';
const source=JSON.parse(await fs.readFile(`${root}/.work_alertes/classified.json`,'utf8'));
const output=`${root}/outputs/alertes_market_20261028`;
await fs.mkdir(output,{recursive:true});
const wb=Workbook.create();
const s=wb.worksheets.add('Alertes_Market');
const headers=['ID de participation','Date de participation','ID PDV','PDV','Secteur','Région','Verbatim','Type de verbatim','overall_sentimant','theme','theme_sentiment'];
const data=[];
function dateSerial(t){const [d,m,y,h,mi,se]=t.split(/[ /:]/).map(Number);return Date.UTC(y,m-1,d,h,mi,se)/86400000+25569;}
for(const x of source){
 const r=x.source;
 for(const [theme,sentiment] of x.themes)data.push([r['ID de participation'],dateSerial(r['Date de participation']),String(r['ID PDV']),r.PDV,r.Secteur,r['Région'],r.Verbatim,r['Type de verbatim'],x.overall,theme,sentiment]);
}
const last=data.length+1;
s.getRange(`A1:K${last}`).values=[headers,...data];
s.showGridLines=false;s.tabColor='#24476A';
const used=s.getRange(`A1:K${last}`);
used.format.font={name:'Arial',size:10,color:'#222222'};
used.format.verticalAlignment='top';used.format.wrapText=true;
s.getRange(`A2:A${last}`).setNumberFormat('@');s.getRange(`C2:C${last}`).setNumberFormat('@');
s.getRange(`B2:B${last}`).setNumberFormat('dd/mm/yyyy hh:mm:ss');
const widths=[22,23,12,27,23,18,110,20,23,46,23];
for(let c=0;c<widths.length;c++)s.getRangeByIndexes(0,c,last,1).format.columnWidth=widths[c];
s.tables.add(`A1:K${last}`,true,'AlertesMarket');
s.getRange('A1:K1').format={fill:'#24476A',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true,verticalAlignment:'center'};
for(let i=0;i<data.length;i++){
 const t=String(data[i][6]||'');
 const lines=t.split(/\r?\n/).reduce((n,line)=>n+Math.max(1,Math.ceil(line.length/125)),0);
 s.getRangeByIndexes(i+1,0,1,11).format.rowHeight=Math.min(409,Math.max(32,lines*13+8));
}
s.freezePanes.freezeRows(1);
const fills={Positif:'#E4F2E7','Négatif':'#FBE9E7',Mixte:'#FFF2CC',Neutre:'#EEF2F6','Non analysable':'#F1F1F1'};
for(const col of ['I','K'])for(const [label,fill] of Object.entries(fills))s.getRange(`${col}2:${col}${last}`).conditionalFormats.add('containsText',{text:label,format:{fill}});
const m=wb.worksheets.add('Lecture');m.showGridLines=false;m.tabColor='#8995A2';
const ids=new Set(source.map(x=>String(x.source['ID PDV'])));
const review=source.filter(x=>x.reviewed).length;
const notes=[
 ['Champ','Description'],
 ['Périmètre','Market uniquement. ID PDV présent dans les codes établissement de nps.xlsx, feuille MARKET (111 codes de référence).'],
 ['Alertes distinctes',source.length],
 ['Magasins présents',ids.size],
 ['Lignes alerte–thème',data.length],
 ['Unité de ligne','Une ligne par alerte et thème. Une alerte multithématique apparaît plusieurs fois. Compter les ID de participation distincts pour compter les alertes.'],
 ['Méthode','Analyse locale par règles lexicales et contextuelles, complétée par une revue ciblée de '+review+' verbatims, notamment des textes en arabe/darija et des cas ambigus. Les autres lignes ne sont pas revues individuellement.'],
 ['Limite','Classification exploratoire, non évaluée sur un jeu de référence métier. Certaines nuances, fautes de frappe, sujets implicites ou sentiments par thème peuvent nécessiter une correction.'],
 ['overall_sentimant','Sentiment du commentaire entier : Positif, Négatif, Mixte, Neutre ou Non analysable. Nom de colonne conservé comme demandé.'],
 ['theme','Sujet abordé par le client. Plusieurs sujets peuvent être attribués au même verbatim.'],
 ['theme_sentiment','Sentiment associé au thème. Une appréciation positive et une critique d’un même thème donnent Mixte. Pour les classifications automatiques, un thème sans polarité locale explicite peut hériter du sentiment global univoque.'],
 ['Neutre','Question, demande ou suggestion sans appréciation positive/négative explicite.'],
 ['Non analysable','Commentaire vide, contenu incompréhensible, coordonnées seules ou texte hors sujet. Les lignes restent présentes.'],
 ['Verbatims vides',source.filter(x=>!String(x.source.Verbatim||'').trim()).length],
 ['Type de verbatim','Catégorie originale conservée pour comparaison. Elle ne détermine pas automatiquement le sentiment.'],
 ['Champs conservés','ID de participation, date, ID PDV, magasin, secteur, région, verbatim et type original, plus les trois colonnes d’analyse.'],
 ['Champs retirés','Colonnes entièrement vides, coordonnées individuelles, métadonnées techniques/redondantes, et réponses/suivi de réponse hors du périmètre de cette analyse. Le texte original des verbatims est conservé.'],
 ['Sources','alertes.xlsx / Export ; nps.xlsx / MARKET. Fichiers sources non modifiés.'],
 ['Dates','Dates et heures de participation reprises de la source, sans conversion de fuseau horaire.']
];
m.getRange(`A1:B${notes.length}`).values=notes;
m.getRange(`A1:B${notes.length}`).format={font:{name:'Arial',size:10,color:'#222222'},wrapText:true,verticalAlignment:'top'};
m.getRange(`A1:A${notes.length}`).format.columnWidth=27;m.getRange(`B1:B${notes.length}`).format.columnWidth=115;
m.getRange('A1:B1').format={fill:'#24476A',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:25};
for(let i=1;i<notes.length;i++)m.getRange(`A${i+1}:B${i+1}`).format.rowHeight=Math.max(28,Math.ceil(String(notes[i][1]).length/125)*14+12);
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Alertes_Market!I1:K5',include:'values',tableMaxRows:5,tableMaxCols:3,maxChars:1800})).ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(`${output}/alertes_market.xlsx`);
for(const [name,range,file] of [['Alertes_Market','G1:K6','preview.png'],['Lecture','A1:B11','method.png']]){
 const im=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(`${root}/.work_alertes/${file}`,new Uint8Array(await im.arrayBuffer()));
}
console.log(JSON.stringify({output:`${output}/alertes_market.xlsx`,alerts:source.length,rows:data.length,stores:ids.size,reviewed:review}));
