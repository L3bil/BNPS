"""Build Market analytical CSVs without changing supplied files.

Run with the bundled Python runtime (requires openpyxl).
"""
from __future__ import annotations
import argparse,calendar,collections,csv,hashlib,json,re,unicodedata
from datetime import date,datetime,timedelta
from pathlib import Path
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
def slug(s):
 s=''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c))
 return re.sub('[^a-z0-9]+','_',s).strip('_')
def sid(v):
 return str(int(v)) if isinstance(v,(float,int)) else str(v).strip().removesuffix('.0')
def number(v):
 if v is None or str(v).strip() in ['','-','--',',','N/A']:return None
 return float(v)
def month_end(y,m):return date(y,m,calendar.monthrange(y,m)[1])
def xrows(path,sheet):
 w=openpyxl.load_workbook(path,read_only=True,data_only=True)
 rows=list(w[sheet].values);w.close();return rows
def write_csv(path,rows,fields=None):
 rows=list(rows)
 if fields is None:fields=list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def read_csv(path):
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def months_between(a,b):
 out=[]
 while a<=b:
  out.append(a.strftime('%Y-%m'));a=date(a.year+(a.month==12),a.month%12+1,1)
 return out
def prior_year(d):return d.replace(year=d.year-1,day=min(d.day,calendar.monthrange(d.year-1,d.month)[1]))

def build(cutoff,output,alert_path):
 output.mkdir(parents=True,exist_ok=True)
 issues=[];corrections=[]
 baro_raw=xrows(ROOT/'baro.xlsx','Super');nps_raw=xrows(ROOT/'nps.xlsx','MARKET')
 metric_headers=baro_raw[0][8:]
 metric_keys=['baro_'+slug(h) for h in metric_headers]
 assert len(set(metric_keys))==len(metric_keys)
 baro=[];baro_long=[]
 waves={'jan_fev':(1,2),'janv_fev':(1,2),'mars_avril':(3,4),'mai_juin':(5,6),'juillet_aout':(7,8),'sept_oct':(9,10),'nov_dec':(11,12)}
 for rownum,r in enumerate(baro_raw[1:],2):
  if not r[4]:continue
  code=sid(r[4]);name=r[5];year=int(r[2]);wave=slug(r[3]);m1,m2=waves[wave]
  original_code=code
  if code=='123' and year==2026 and m1==5 and str(name).strip()=='SALA EL JADIDA (123)':
   code='122';name='SALA EL JADIDA'
   corrections.append({'source':'baro.xlsx','sheet':'Super','source_row':rownum,'field':'Code Site / Magasin','old_value':'123 / SALA EL JADIDA (123)','new_value':'122 / SALA EL JADIDA','reason':'User confirmed 123 belongs to VALFLEURY and SALA row is a typo; 122 matches all other waves and NPS.'})
  start=date(year,m1,1);end=month_end(year,m2);period_id=f'{year}-{m1:02d}_{year}-{m2:02d}'
  entry={'store_id':code,'store_name':name,'cluster':str(r[1]).strip().upper(),'city':r[6],'city_classification':r[7],'period_id':period_id,'period_label':str(r[3]).strip(),'period_start':start,'period_end':end,'source_row':rownum,'original_store_id':original_code}
  for k,h,v in zip(metric_keys,metric_headers,r[8:]):
   value=number(v)
   if value is not None and not -600-1e-8<=value<=300+1e-8:raise ValueError(('score out of range',rownum,h,value))
   entry[k]=value
   baro_long.append({'store_id':code,'period_id':period_id,'period_start':start,'period_end':end,'indicator_id':k,'indicator_label':h,'score':value,'source_row':rownum,'source_value':v})
  entry['survey_available']=entry['baro_score_global'] is not None
  baro.append(entry)
 assert len({(x['store_id'],x['period_id']) for x in baro})==len(baro),'Conflicting store-wave key'
 nps=[]
 for rownum,r in enumerate(nps_raw[1:],2):
  label=str(r[0]);nums=[number(v) for v in r[7:12]]
  if label.startswith('S1'):start=date(int(label[-4:]),1,1);end=date(start.year,6,30)
  elif label.startswith('S2'):start=date(int(label[-4:]),7,1);end=date(start.year,12,31)
  elif label=='Juillet-23 octobre 2026':start=date(2026,7,1);end=date(2026,10,23)
  else:raise ValueError(label)
  entry={'store_id':sid(r[3]),'store_name':r[4],'sector':r[5],'period_id':f'{start.isoformat()}_{end.isoformat()}','period_label':label,'period_start':start,'period_end':end,'nps':nums[1],'participation_count':int(nums[0]) if nums[0] is not None else None,'detractor_pct':nums[2],'passive_pct':nums[3],'promoter_pct':nums[4],'survey_available':nums[1] is not None,'source_row':rownum}
  if nums[1] is not None:
   assert -100<=nums[1]<=100
   assert nums[0]>0 and all(0<=v<=1 for v in nums[2:])
   entry['nps_from_rounded_shares']=100*(nums[4]-nums[2])
   entry['nps_rounding_difference']=nums[1]-entry['nps_from_rounded_shares']
  nps.append(entry)
 assert len({(x['store_id'],x['period_id']) for x in nps})==len(nps)
 baro_ids={x['store_id'] for x in baro};nps_ids={x['store_id'] for x in nps};all_ids=baro_ids|nps_ids
 perf={};monthly=[]
 for rownum,r in enumerate(read_csv(ROOT/'monthly_performance.csv'),2):
  code=sid(r['store_code'])
  if code not in all_ids:continue
  key=(code,r['month']);assert key not in perf
  start=datetime.strptime(r['month'],'%Y-%m').date();end=month_end(start.year,start.month)
  sales=number(r['sales']);tickets=number(r['ticket_count']);assert sales is not None and tickets is not None and tickets>0
  entry={'store_id':code,'month':r['month'],'period_start':start,'period_end':min(end,cutoff),'sales':sales,'ticket_count':int(tickets),'average_basket':sales/tickets,'average_basket_source_rounded':number(r['average_basket']),'month_complete':end<=cutoff,'source_row':rownum}
  assert start<=cutoff
  perf[key]=entry;monthly.append(entry)
 alerts_source=xrows(alert_path,'Alertes_Market');ah=alerts_source[0];alerts={};themes=[]
 for row in alerts_source[1:]:
  r=dict(zip(ah,row));key=r['ID de participation'];code=sid(r['ID PDV']);assert code in nps_ids
  dt=r['Date de participation'];assert isinstance(dt,datetime)
  a={'alert_id':key,'store_id':code,'store_name':r['PDV'],'participation_datetime':dt.isoformat(sep=' '),'participation_date':dt.date(),'sector':r['Secteur'],'region':r['Région'],'verbatim':r['Verbatim'],'original_type':r['Type de verbatim'],'overall_sentiment':r['overall_sentimant']}
  if key in alerts:assert alerts[key]==a
  else:alerts[key]=a
  themes.append({'alert_id':key,'store_id':code,'participation_date':dt.date(),'theme_id':slug(r['theme']),'theme':r['theme'],'theme_sentiment':r['theme_sentiment']})
 assert len({(x['alert_id'],x['theme_id']) for x in themes})==len(themes)
 theme_dict={x['theme_id']:x['theme'] for x in themes}
 alert_by_store=collections.defaultdict(list);themes_by_alert=collections.defaultdict(list)
 for a in alerts.values():alert_by_store[a['store_id']].append(a)
 for t in themes:themes_by_alert[t['alert_id']].append(t)
 def performance(code,start,end):
  expected=months_between(start,end);present=[perf[(code,m)] for m in expected if (code,m) in perf]
  missing=[m for m in expected if (code,m) not in perf]
  mismatch=[p['month'] for p in present if p['period_start']<start or p['period_end']>end or p['period_end']<min(month_end(p['period_start'].year,p['period_start'].month),end)]
  status='aligned' if not missing and not mismatch else ('missing_months_and_period_mismatch' if missing and mismatch else 'missing_months' if missing else 'period_mismatch')
  sales=sum(p['sales'] for p in present) if status=='aligned' else None
  tickets=sum(p['ticket_count'] for p in present) if status=='aligned' else None
  return {'performance_status':status,'performance_months_expected':len(expected),'performance_months_present':len(present),'missing_performance_months':'|'.join(missing),'mismatched_performance_months':'|'.join(mismatch),'sales':sales,'ticket_count':tickets,'average_basket':sales/tickets if tickets else None}
 long_summaries=[]
 def enrich(rows,source_name):
  out=[]
  for original in rows:
   r=dict(original);code=r['store_id'];start=r['period_start'];end=r['period_end']
   r['period_days']=(end-start).days+1
   r.update(performance(code,start,end))
   py=performance(code,prior_year(start),prior_year(end));r['prior_year_performance_status']=py['performance_status']
   for key in ['sales','ticket_count','average_basket']:
    r[key+'_prior_year']=py[key]
    r[key+'_yoy_pct']=(r[key]/py[key]-1)*100 if r[key] is not None and py[key] else None
   selected=[a for a in alert_by_store[code] if start<=a['participation_date']<=end]
   r['alert_count']=len(selected)
   r['alerts_with_text_count']=sum(bool(str(a['verbatim'] or '').strip()) for a in selected)
   r['alerts_analysable_count']=sum(a['overall_sentiment']!='Non analysable' for a in selected)
   for label,key in [('Positif','positive'),('Négatif','negative'),('Mixte','mixed'),('Neutre','neutral'),('Non analysable','not_analysable')]:
    r['alerts_'+key+'_count']=sum(a['overall_sentiment']==label for a in selected)
   r['negative_alert_share_pct']=100*r['alerts_negative_count']/r['alerts_analysable_count'] if r['alerts_analysable_count'] else None
   r['has_recorded_alerts']=bool(selected)
   r['alerts_id_in_reference']=code in nps_ids
   r['commercial_comparison_ready']=r['survey_available'] and r['performance_status']=='aligned'
   by_theme=collections.defaultdict(list)
   for a in selected:
    for t in themes_by_alert[a['alert_id']]:by_theme[t['theme_id']].append(t)
   for tid in sorted(theme_dict):
    ts=by_theme[tid];count=len(ts);negative=sum(t['theme_sentiment']=='Négatif' for t in ts)
    r['theme_'+tid+'_mentions']=count;r['theme_'+tid+'_negative_mentions']=negative
    if count:long_summaries.append({'survey_source':source_name,'store_id':code,'period_id':r['period_id'],'period_start':start,'period_end':end,'theme_id':tid,'theme':theme_dict[tid],'alert_mentions':count,'negative_mentions':negative,'positive_mentions':sum(t['theme_sentiment']=='Positif' for t in ts),'mixed_mentions':sum(t['theme_sentiment']=='Mixte' for t in ts),'neutral_mentions':sum(t['theme_sentiment']=='Neutre' for t in ts),'not_analysable_mentions':sum(t['theme_sentiment']=='Non analysable' for t in ts),'share_of_recorded_alerts_pct':count/len(selected)*100})
   if r['performance_status']!='aligned':issues.append({'source':source_name,'store_id':code,'period_id':r['period_id'],'issue':r['performance_status'],'details':'missing='+r['missing_performance_months']+'; mismatch='+r['mismatched_performance_months']})
   if not r['survey_available']:issues.append({'source':source_name,'store_id':code,'period_id':r['period_id'],'issue':'survey_score_missing','details':'Source score unavailable; retained as missing.'})
   out.append(r)
  return sorted(out,key=lambda r:(r['store_id'],r['period_start']))
 ba=enrich(baro,'barometre');na=enrich(nps,'nps')
 # Deltas are only defined for consecutive reported periods, never across missing waves.
 for rows,metric in [(ba,'baro_score_global'),(na,'nps')]:
  previous={}
  for r in rows:
   p=previous.get(r['store_id']);r['previous_survey_period_id']=p['period_id'] if p else None
   adjacent=p is not None and p['period_end']+timedelta(days=1)==r['period_start']
   comparable=adjacent and p['period_days']==r['period_days']
   r['previous_period_adjacent']=adjacent;r['previous_period_same_day_count']=comparable
   for key in (metric_keys if metric=='baro_score_global' else ['nps']):
    r[key+'_change_previous_period']=r[key]-p[key] if adjacent and r[key] is not None and p[key] is not None else None
   previous[r['store_id']]=r
 stores=[]
 for code in sorted(all_ids):
  br=sorted([r for r in baro if r['store_id']==code],key=lambda x:x['period_end']);nr=sorted([r for r in nps if r['store_id']==code],key=lambda x:x['period_end']);pr=sorted([r for r in monthly if r['store_id']==code],key=lambda x:x['month'])
  stores.append({'store_id':code,'store_name_nps':nr[-1]['store_name'] if nr else None,'store_name_barometre':br[-1]['store_name'] if br else None,'in_barometre_super':code in baro_ids,'in_nps_market':code in nps_ids,'in_alerts':code in alert_by_store,'in_performance':bool(pr),'latest_baro_cluster':br[-1]['cluster'] if br else None,'latest_baro_city':br[-1]['city'] if br else None,'performance_first_month':pr[0]['month'] if pr else None,'performance_last_month':pr[-1]['month'] if pr else None,'performance_month_count':len(pr)})
 outputs={
  'stores_market.csv':stores,'monthly_performance_market.csv':sorted(monthly,key=lambda x:(x['store_id'],x['month'])),
  'barometre_market_long.csv':baro_long,'nps_market.csv':nps,'alerts_market.csv':alerts.values(),'alert_themes_market.csv':themes,
  'barometre_market_analytical.csv':ba,'nps_market_analytical.csv':na,'period_theme_summary.csv':long_summaries,
  'barometre_indicator_dictionary.csv':[{'indicator_id':k,'original_label':h,'scale_min':-600,'scale_max':300} for k,h in zip(metric_keys,metric_headers)],
  'theme_dictionary.csv':[{'theme_id':k,'theme':v} for k,v in sorted(theme_dict.items())],
  'data_quality_issues.csv':issues,'source_corrections.csv':corrections,
 }
 for name,rows in outputs.items():write_csv(output/name,rows)
 report={
  'transaction_cutoff_inclusive':cutoff.isoformat(),'barometre_store_count':len(baro_ids),'nps_store_count':len(nps_ids),'reference_union_store_count':len(all_ids),
  'barometre_only_ids':sorted(baro_ids-nps_ids),'nps_only_ids':sorted(nps_ids-baro_ids),'nps_ids_missing_performance':sorted(nps_ids-{r['store_id'] for r in monthly}),
  'barometre_rows':len(ba),'barometre_indicators':len(metric_keys),'barometre_missing_score_cells':sum(r['score'] is None for r in baro_long),
  'nps_rows':len(na),'nps_missing_scores':sum(not r['survey_available'] for r in na),'unique_alerts':len(alerts),'alert_theme_rows':len(themes),
  'barometre_commercial_comparisons_ready':sum(r['commercial_comparison_ready'] for r in ba),'nps_commercial_comparisons_ready':sum(r['commercial_comparison_ready'] for r in na),
  'barometre_performance_status':dict(collections.Counter(r['performance_status'] for r in ba)),
  'nps_performance_status':dict(collections.Counter(r['performance_status'] for r in na)),
  'source_corrections':corrections,
  'inputs':[{'file':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [ROOT/'baro.xlsx',ROOT/'nps.xlsx',ROOT/'monthly_performance.csv',alert_path]],
 }
 (output/'quality_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 definitions={
  'store_id':'Canonical store code, stored as text. Joins use codes, not store names.',
  'period_id':'Survey-specific period identifier. Unique with store_id within each main analytical file.',
  'period_start':'First calendar date represented by the survey label; actual fieldwork dates were not supplied.',
  'period_end':'Last calendar date represented by the survey label, inclusive.',
  'period_days':'Number of calendar days in the survey period, inclusive.',
  'source_row':'One-based source Excel row number, including header.',
  'original_store_id':'Uncorrected Barometre store code; see source_corrections.csv.',
  'survey_available':'Whether the source global Barometre score or NPS score is present.',
  'nps':'Original NPS score, -100 to +100; not recalculated from rounded percentages.',
  'participation_count':'Number of NPS responses in this store-period. Missing remains blank.',
  'detractor_pct':'Original detractor proportion stored on a 0–1 scale.',
  'passive_pct':'Original passive proportion stored on a 0–1 scale.',
  'promoter_pct':'Original promoter proportion stored on a 0–1 scale.',
  'nps_from_rounded_shares':'100 × (promoter_pct − detractor_pct), for comparison only.',
  'nps_rounding_difference':'Source NPS minus NPS calculated from the rounded source proportions.',
  'performance_status':'aligned, missing_months, period_mismatch, or missing_months_and_period_mismatch.',
  'performance_months_expected':'Number of calendar months touched by the survey period.',
  'performance_months_present':'Number of corresponding monthly transaction rows found.',
  'missing_performance_months':'Missing YYYY-MM keys separated by |. No zero imputation.',
  'mismatched_performance_months':'Monthly rows whose actual coverage cannot exactly match the survey period.',
  'sales':'Sum of source sales for an exactly aligned complete period, in unchanged source monetary units; otherwise blank.',
  'ticket_count':'Sum of transaction tickets for an exactly aligned complete period; business definition of fréquentation.',
  'average_basket':'Period sales divided by period ticket_count, using unrounded totals.',
  'prior_year_performance_status':'Alignment and completeness status for the corresponding calendar dates one year earlier.',
  'alert_count':'Number of distinct supplied alert IDs dated within the period, regardless of theme count.',
  'alerts_with_text_count':'Number of supplied alerts with a nonempty original verbatim.',
  'alerts_analysable_count':'Number of alerts whose overall sentiment is not Non analysable.',
  'negative_alert_share_pct':'100 × negative alert count / analysable alert count; blank when denominator is zero. Describes supplied alerts only.',
  'has_recorded_alerts':'At least one supplied alert falls in the store-period.',
  'alerts_id_in_reference':'Store appears in the NPS MARKET ID list used to filter the supplied labelled alerts. False means that store was outside the alerts-preparation scope.',
  'commercial_comparison_ready':'Source survey score exists and transaction coverage matches the entire survey period exactly. Does not certify statistical reliability.',
  'previous_survey_period_id':'Previous available period for this store in the same source.',
  'previous_period_adjacent':'Previous period ends on the calendar day immediately before this period begins.',
  'previous_period_same_day_count':'Previous period is adjacent and has the same number of calendar days. False does not imply invalid scores.',
 }
 dictionary=[]
 for dataset,records in [('barometre_market_analytical.csv',ba),('nps_market_analytical.csv',na)]:
  for field in dict.fromkeys(k for row in records for k in row):
   desc=definitions.get(field)
   if field in metric_keys:desc='Original Baromètre indicator score, −600 to +300: '+metric_headers[metric_keys.index(field)]+'. Missing markers remain blank.'
   elif field.endswith('_change_previous_period'):desc='Difference in score points versus the immediately adjacent previous survey period. Blank if a score or intervening period is missing. Period length/population may differ.'
   elif field.endswith('_prior_year'):desc='Same-period prior-year value, using exactly aligned available transaction months; otherwise blank.'
   elif field.endswith('_yoy_pct'):desc='100 × (current value / same-period prior-year value − 1). Blank unless both periods are aligned and the prior value is nonzero.'
   elif field.startswith('theme_'):
    suffix='_negative_mentions' if field.endswith('_negative_mentions') else '_mentions';tid=field[6:-len(suffix)]
    desc=('Distinct alerts with negative theme sentiment: ' if suffix=='_negative_mentions' else 'Distinct alerts mentioning: ')+theme_dict[tid]+'. A multi-theme alert can contribute once to several theme columns; do not sum themes to count alerts.'
   elif field.startswith('alerts_') and field.endswith('_count'):desc='Distinct alert count for this overall sentiment category; mutually exclusive across the five sentiment categories.'
   if not desc:desc='Source descriptive field, preserved for this survey period.'
   dictionary.append({'dataset':dataset,'column':field,'definition':desc})
 write_csv(output/'data_dictionary.csv',dictionary)
 # Exploratory examples, limited to adjacent waves with exact commercial alignment.
 latest=max(r['period_end'] for r in ba)
 declines=sorted([r for r in ba if r['period_end']==latest and r['baro_score_global_change_previous_period'] is not None],key=lambda r:r['baro_score_global_change_previous_period'])[:5]
 example_lines=['| Store | Wave | Global score | Change vs previous wave | Sales YoY | Tickets YoY |','|---|---|---:|---:|---:|---:|']
 fmt=lambda v: 'n/a' if v is None else f'{v:.1f}'
 for r in declines:example_lines.append(f"| {r['store_id']} — {r['store_name']} | {r['period_label']} {r['period_start'].year} | {fmt(r['baro_score_global'])} | {fmt(r['baro_score_global_change_previous_period'])} | {fmt(r['sales_yoy_pct'])}% | {fmt(r['ticket_count_yoy_pct'])}% |")
 readme=f'''# Market analytical datasets

Prepared from the supplied files. Transaction cutoff: **{cutoff.isoformat()}, inclusive**.

## Start here

- `barometre_market_analytical.csv`: **{len(ba):,} store × wave rows**, all 35 scores, aligned commercial totals, prior-year changes, sequential score changes, and alert/theme counts.
- `nps_market_analytical.csv`: **{len(na):,} store × NPS-period rows**, source NPS and participation data, the same commercial and alert measures.
- Filter `commercial_comparison_ready=True` for satisfaction-versus-performance analysis: **{report['barometre_commercial_comparisons_ready']:,} Baromètre rows** and **{report['nps_commercial_comparisons_ready']:,} NPS rows**.
- Read `data_dictionary.csv` for every analytical column. Blank CSV values mean unavailable, never zero.

## Source scope and joins

Baromètre uses `baro.xlsx / Super` (114 IDs). NPS uses `nps.xlsx / MARKET` (111 IDs). Their union contains 126 IDs; each source keeps its specified scope rather than dropping stores absent from the other source. The store reference includes membership flags. It is not a list of 126 currently active Market stores.

Transactions are filtered to that union. Alerts retain their established filter to NPS MARKET IDs. For Baromètre-only IDs, `alerts_id_in_reference=False`; zero matched alert rows must not be interpreted as proof of no complaints. Store names are descriptive; joins use store IDs.

The May–June 2026 row labelled SALA EL JADIDA (123) was corrected to store 122. Store 123 remains VALFLEURY. This follows the user's clarification and the code used for SALA EL JADIDA in all other waves and NPS. The source Excel file is unchanged. See `source_corrections.csv`.

## Time alignment

Survey periods keep their original granularity. Dates are interpreted from wave/period labels; fieldwork and publication dates were not supplied. We do not create artificial monthly survey results.

Monthly transactions are summed only when all months exist and their coverage matches the whole survey period. Basket value is total sales / total tickets, not an average of monthly averages. The source sales unit is preserved; the currency and sales-accounting basis have not been independently confirmed.

The latest NPS covers 1 July–23 October 2026, but October transactions cover 1–26 October. Its commercial totals and YoY changes remain blank. July–September totals have not been substituted for the full NPS period. The source survey score and aligned alert summaries remain available.

Earlier missing transaction months also leave period totals blank. We do not infer store openings/closures from these gaps. Prior-year changes require both aligned periods. Score changes require adjacent waves and available scores; compare different NPS period lengths cautiously.

## Alerts and themes

The labelled workbook contains **{len(alerts):,} unique alerts** and **{len(themes):,} alert–theme pairs**. `alerts_market.csv` has one row per alert; `alert_themes_market.csv` has one row per alert and theme. The original label column `overall_sentimant` is standardized to `overall_sentiment` in these CSVs. Labels are inherited, not reclassified by this script.

Period counts deduplicate by alert ID. Theme counts can overlap. Negative-alert share uses analysable alerts as its denominator; theme share uses all recorded alerts in the same period. Mixed sentiment stays separate from negative. Zero means no matching record in the supplied extract, not verified absence of customer problems. `Non analysable` remains separate from neutral.

The sentiment/theme labels are exploratory rule-based classifications with targeted contextual review, as documented in the supplied labelled workbook. They need business validation before operational alerts or model evaluation.

## Data-quality results

- {report['barometre_missing_score_cells']:,} missing Baromètre indicator cells retained as blanks; global scores are available for all {len(ba):,} rows.
- {report['nps_missing_scores']} NPS rows have no source score; those store-period rows remain present.
- NPS IDs with no transaction rows: {', '.join(report['nps_ids_missing_performance'])}.
- Transaction alignment statuses, Baromètre: {report['barometre_performance_status']}.
- Transaction alignment statuses, NPS: {report['nps_performance_status']}.
- NPS shares are rounded in the source. Keep the supplied NPS; the rounded-share reconstruction is diagnostic, not a replacement. Exact promoter/detractor counts were not invented.
- Key uniqueness, source-value preservation, alert deduplication, sentiment counts, and basket calculations are checked during preparation. Input hashes are recorded in `quality_report.json`.

## First exploratory comparison

Largest global-score declines among stores present in the latest Baromètre wave, with an adjacent prior wave. These are descriptive changes, not statistically confirmed anomalies. The score change is versus the previous wave; commercial changes are versus the same period last year.

{chr(10).join(example_lines)}

## Supporting files

`stores_market.csv`, `monthly_performance_market.csv`, `barometre_market_long.csv`, `nps_market.csv`, `alerts_market.csv`, `alert_themes_market.csv`, `period_theme_summary.csv`, and the two dictionaries retain reusable components and source lineage. `data_quality_issues.csv` lists affected store-periods; `quality_report.json` provides counts and input hashes.

## Refresh

Run `scripts/prepare_market.py` from this project using Python with openpyxl. Default cutoff is 2026-10-26; pass `--transaction-cutoff YYYY-MM-DD` when the source changes. The cutoff applies to the latest partial calendar month. Default outputs are in `outputs/market_analytical`. Input files are not modified.

## Next analysis

Review stores with simultaneous score deterioration and declining same-period sales/tickets. Compare like formats/clusters, inspect detailed topic scores and supporting verbatims, and validate a sample of classifications with the business. These datasets support exploratory association; they do not establish causality or validated future prediction. Publication dates, survey sample sizes, and more temporal observations would be needed for rigorous forecasting.
'''
 (output/'README.md').write_text(readme,encoding='utf-8')
 # Reconcile counts from the unique alert table, not repeated alert-theme rows.
 for rows in [ba,na]:
  for r in rows:
   assert sum(r['alerts_'+k+'_count'] for k in ['positive','negative','mixed','neutral','not_analysable'])==r['alert_count']
   assert r['alerts_analysable_count']+r['alerts_not_analysable_count']==r['alert_count']
   if r['performance_status']=='aligned':assert abs(r['average_basket']-r['sales']/r['ticket_count'])<1e-9
   else:assert r['sales'] is None and r['ticket_count'] is None and r['average_basket'] is None
   for tid in theme_dict:assert r['theme_'+tid+'_negative_mentions']<=r['theme_'+tid+'_mentions']<=r['alert_count']
 assert len(ba)==1533 and len(na)==444 and len(alerts)==3691
 print(json.dumps({k:v for k,v in report.items() if k not in ['inputs','source_corrections']},ensure_ascii=False,indent=2))
 return report

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--transaction-cutoff',default='2026-10-26');parser.add_argument('--output',type=Path,default=ROOT/'outputs'/'market_analytical');parser.add_argument('--alerts',type=Path,default=ROOT/'outputs'/'alertes_market_20261028'/'alertes_market.xlsx')
 args=parser.parse_args();build(date.fromisoformat(args.transaction_cutoff),args.output,args.alerts)
