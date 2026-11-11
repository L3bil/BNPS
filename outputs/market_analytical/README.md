# Market analytical datasets

Prepared from the supplied files. Transaction cutoff: **2026-10-26, inclusive**.

## Start here

- `barometre_market_analytical.csv`: **1,533 store × wave rows**, all 35 scores, aligned commercial totals, prior-year changes, sequential score changes, and alert/theme counts.
- `nps_market_analytical.csv`: **444 store × NPS-period rows**, source NPS and participation data, the same commercial and alert measures.
- Filter `commercial_comparison_ready=True` for satisfaction-versus-performance analysis: **1,533 Baromètre rows** and **265 NPS rows**.
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

The labelled workbook contains **3,691 unique alerts** and **6,191 alert–theme pairs**. `alerts_market.csv` has one row per alert; `alert_themes_market.csv` has one row per alert and theme. The original label column `overall_sentimant` is standardized to `overall_sentiment` in these CSVs. Labels are inherited, not reclassified by this script.

Period counts deduplicate by alert ID. Theme counts can overlap. Negative-alert share uses analysable alerts as its denominator; theme share uses all recorded alerts in the same period. Mixed sentiment stays separate from negative. Zero means no matching record in the supplied extract, not verified absence of customer problems. `Non analysable` remains separate from neutral.

The sentiment/theme labels are exploratory rule-based classifications with targeted contextual review, as documented in the supplied labelled workbook. They need business validation before operational alerts or model evaluation.

## Data-quality results

- 2,029 missing Baromètre indicator cells retained as blanks; global scores are available for all 1,533 rows.
- 59 NPS rows have no source score; those store-period rows remain present.
- NPS IDs with no transaction rows: 659, 707, 722, 725, 740, 749, 754, 768.
- Transaction alignment statuses, Baromètre: {'aligned': 1533}.
- Transaction alignment statuses, NPS: {'aligned': 295, 'period_mismatch': 97, 'missing_months': 52}.
- NPS shares are rounded in the source. Keep the supplied NPS; the rounded-share reconstruction is diagnostic, not a replacement. Exact promoter/detractor counts were not invented.
- Key uniqueness, source-value preservation, alert deduplication, sentiment counts, and basket calculations are checked during preparation. Input hashes are recorded in `quality_report.json`.

## First exploratory comparison

Largest global-score declines among stores present in the latest Baromètre wave, with an adjacent prior wave. These are descriptive changes, not statistically confirmed anomalies. The score change is versus the previous wave; commercial changes are versus the same period last year.

| Store | Wave | Global score | Change vs previous wave | Sales YoY | Tickets YoY |
|---|---|---:|---:|---:|---:|
| 7107 — Jnan Gueliz  | Juillet-Août 2026 | 211.2 | -54.0 | 25.5% | 24.0% |
| 742 — Ouled Salah | Juillet-Août 2026 | 223.4 | -44.1 | 45.2% | 29.7% |
| 179 — Bellerive | Juillet-Août 2026 | 210.6 | -36.4 | 1.5% | 5.0% |
| 117 — Fes Immouzzer | Juillet-Août 2026 | 234.3 | -36.2 | 9.2% | 11.8% |
| 120 — MAARIF | Juillet-Août 2026 | 226.6 | -35.3 | 2.7% | 10.4% |

## Supporting files

`stores_market.csv`, `monthly_performance_market.csv`, `barometre_market_long.csv`, `nps_market.csv`, `alerts_market.csv`, `alert_themes_market.csv`, `period_theme_summary.csv`, and the two dictionaries retain reusable components and source lineage. `data_quality_issues.csv` lists affected store-periods; `quality_report.json` provides counts and input hashes.

## Refresh

Run `scripts/prepare_market.py` from this project using Python with openpyxl. Default cutoff is 2026-10-26; pass `--transaction-cutoff YYYY-MM-DD` when the source changes. The cutoff applies to the latest partial calendar month. Default outputs are in `outputs/market_analytical`. Input files are not modified.

## Next analysis

Review stores with simultaneous score deterioration and declining same-period sales/tickets. Compare like formats/clusters, inspect detailed topic scores and supporting verbatims, and validate a sample of classifications with the business. These datasets support exploratory association; they do not establish causality or validated future prediction. Publication dates, survey sample sizes, and more temporal observations would be needed for rigorous forecasting.
