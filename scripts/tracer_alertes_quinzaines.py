from pathlib import Path
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'alertes_quinzaines'
OUT.mkdir(parents=True, exist_ok=True)
d = pd.read_excel(ROOT / 'alertes-market.xlsx')
assert d.ID_de_participation.notna().all()
assert d.groupby('ID_de_participation').Date_de_participation.nunique().max() == 1
d = d.drop_duplicates('ID_de_participation')
dates = pd.to_datetime(d.Date_de_participation, errors='raise').dt.normalize()
assert dates.notna().all()
start, last = dates.min(), dates.max()
bins = ((dates - start).dt.days // 14)
counts = bins.value_counts().reindex(range(int(bins.max()) + 1), fill_value=0).sort_index()
r = pd.DataFrame({'debut': start + pd.to_timedelta(counts.index * 14, unit='D'), 'nombre_alertes': counts.values})
r['fin'] = r.debut + pd.Timedelta(days=13)
r['derniere_date_observee'] = r.fin.clip(upper=last)
assert r.nombre_alertes.sum() == len(d)
r[['debut', 'fin', 'derniere_date_observee', 'nombre_alertes']].to_csv(OUT / 'alertes_par_14_jours.csv', index=False, encoding='utf-8-sig')

im = Image.new('RGB', (2000, 900), '#f8fafc')
g = ImageDraw.Draw(im)
def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/' + ('arialbd.ttf' if bold else 'arial.ttf'), size)
def txt(x, y, value, size=22, color='#536579', bold=False):
    g.text((x, y), str(value), font=font(size, bold), fill=color)
txt(100, 40, 'Market — Nombre d’alertes par période de 14 jours', 38, '#102e4b', True)
txt(100, 100, f'{len(d):,} alertes uniques • Du {start:%d/%m/%Y} au {last:%d/%m/%Y} • Tous sentiments'.replace(',', ' '), 25)
left, right, top, bottom = 100, 1940, 175, 650
ceiling = math.ceil(r.nombre_alertes.max() / 50) * 50
for value in range(0, ceiling + 1, 50):
    y = bottom - value / ceiling * (bottom-top)
    g.line((left, y, right, y), fill='#dce4ed', width=1)
    txt(30, y-13, value, 20)
w = (right-left) / len(r)
for i, row in r.iterrows():
    x = left+i*w
    y = bottom-row.nombre_alertes/ceiling*(bottom-top)
    color = '#ee9b36' if i == len(r)-1 and last < row.fin else '#1676ba'
    if row.nombre_alertes > 0: g.rectangle((x+2, y, x+w-2, bottom), fill=color)
    if i % 6 == 0:
        label=Image.new('RGBA', (165, 32), (0,0,0,0))
        ImageDraw.Draw(label).text((0,0), row.debut.strftime('%d/%m/%Y'), font=font(20), fill='#536579')
        label=label.rotate(35, expand=True)
        im.paste(label, (int(x)-75, bottom+10), label)
txt(100, 145, 'Nombre d’alertes uniques', 20)
txt(760, 770, 'Début de chaque période de 14 jours', 23)
txt(100, 820, 'Source : alertes-market.xlsx. Une alerte = un ID de participation, même avec plusieurs thèmes.', 20)
if last < r.fin.iloc[-1]:
    txt(100, 850, f'Orange : période du {r.debut.iloc[-1]:%d/%m} au {r.fin.iloc[-1]:%d/%m/%Y}, données jusqu’au {last:%d/%m}.', 20)
im.save(OUT / 'alertes_par_14_jours.png')
print(r.tail().to_string(index=False))
print('Total :', len(d))

