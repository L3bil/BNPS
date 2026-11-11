"""Usage Spark : resultats = analyser(final_df). Conversion locale des colonnes utiles."""
import pandas as pd
import numpy as np
from pathlib import Path

IND=['alerts_count','global_score','satisfaction_score','nps_score']
PERF=['sales','ticket_count','average_basket']

def residus(d,cols):
 x=d[cols].astype(float).copy()
 for _ in range(100):
  old=x.copy()
  for g in ['store_id','month']:
   x-=x.groupby(d[g]).transform('mean')
  if np.max(np.abs(x-old).to_numpy())<1e-9:break
 return x

def analyser(final_df):
 cols=['store_id','month']+IND+PERF
 d=final_df.select(*cols).toPandas() if hasattr(final_df,'toPandas') else final_df[cols].copy()
 d['month']=pd.to_datetime(d.month).dt.to_period('M')
 for c in IND+PERF:d[c]=pd.to_numeric(d[c],errors='coerce')
 if d.duplicated(['store_id','month']).any():
  d=d.groupby(['store_id','month'],as_index=False).agg({c:lambda s:s.iloc[0] if s.nunique(dropna=False)==1 else np.nan for c in IND+PERF})
 d=d.sort_values(['store_id','month'])
 d['alerts_count']=d.alerts_count*10000/d.ticket_count.where(d.ticket_count>0)
 past=d[['store_id','month']+PERF].copy();past['month']+=12
 d=d.merge(past,on=['store_id','month'],how='left',suffixes=('','_n1'))
 for c in PERF:d[c+'_yoy']=100*(d[c]/d[c+'_n1'].where(d[c+'_n1']>0)-1)
 # Octobre 2026 : transactions arrêtées au 26 inclus.
 d.loc[d.month==pd.Period('2026-10'),[c+'_yoy' for c in PERF]]=np.nan
 out=[]
 for ind in IND:
  if ind=='alerts_count':a=d.copy();step=1
  elif ind=='nps_score':a=d[(d.month.dt.month.isin([6,12])) | (d.month==pd.Period('2026-10'))].copy();step=6
  else:a=d[d.month.dt.month%2==0].copy();step=2
  a=a[a[ind].notna()].copy()
  prev=a.groupby('store_id')[ind].shift();pm=a.groupby('store_id').month.shift()
  adjacent=a.month.astype('int64')-pm.map(lambda v:v.ordinal if pd.notna(v) else np.nan)==step
  a['variation']=(a[ind]-prev).where(adjacent)
  # Seuils contemporains : quartile haut des alertes, quartile bas des scores.
  q=a.groupby('month')[ind].transform(lambda x:x.quantile(.75 if ind=='alerts_count' else .25))
  a['segment']=a[ind]>=q if ind=='alerts_count' else a[ind]<=q
  for lag in [1,2,3]:
   future=d[['store_id','month']+[c+'_yoy' for c in PERF]].copy();future['month']-=lag
   z=a.merge(future,on=['store_id','month'],suffixes=('','_futur'))
   for target in PERF:
    y=target+'_yoy_futur'
    z['delta_y']=z[y]-z[target+'_yoy']
    for method,mask,xcol,ycol in [('Décalage',pd.Series(True,index=z.index),ind,y),('Intra-magasin',pd.Series(True,index=z.index),'variation','delta_y'),('Segment défavorable',z.segment,ind,y),('Autres magasins',~z.segment,ind,y)]:
     s=z.loc[mask,['store_id','month',xcol,ycol]].dropna()
     if method=='Intra-magasin':
      s=s[s.groupby('store_id').store_id.transform('size')>=2]
      vals=residus(s,[xcol,ycol]) if len(s) else s[[xcol,ycol]]
     else:vals=s[[xcol,ycol]]
     r=vals[xcol].corr(vals[ycol]) if len(s)>2 and vals[xcol].std()>1e-8 and vals[ycol].std()>1e-8 else np.nan
     out.append({'analyse':method,'indicateur':ind,'performance':target,'decalage_mois':lag,'n':len(s),'magasins':s.store_id.nunique(),'periodes':s.month.nunique(),'r':round(r,3) if pd.notna(r) else None,'statut':'Insuffisant' if len(s)<30 or s.store_id.nunique()<10 or s.month.nunique()<3 or pd.isna(r) else 'Descriptif'})
 resultats=pd.DataFrame(out)
 resultats.loc[(resultats.indicateur=='nps_score') & (resultats.periodes<6),'statut']='Insuffisant : moins de 6 périodes NPS'
 return resultats

if __name__=='__main__':
 root=Path(__file__).resolve().parents[1];out=root/'outputs/relations_satisfaction';out.mkdir(exist_ok=True)
 d=pd.read_csv(root/'final_df.csv',na_values=['null'])
 r=analyser(d);r.to_csv(out/'resultats.csv',index=False,encoding='utf-8-sig')
 print(r.groupby(['analyse','indicateur']).agg(n_min=('n','min'),n_max=('n','max'),r_min=('r','min'),r_max=('r','max')).to_string())
 print('Meilleurs coefficients descriptifs :')
 print(r[r.statut=='Descriptif'].assign(abs_r=lambda x:x.r.abs()).nlargest(8,'abs_r').to_string(index=False))
 print('Manquants :',d[IND].isna().sum().to_dict())
