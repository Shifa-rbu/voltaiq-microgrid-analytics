# VoltaIQ — Campus Energy Workbench

VoltaIQ is an educational prototype for a campus facilities team to inspect meter readings, understand usage patterns, and estimate costs from explicit tariff assumptions. The intended workflow is **Overview → Data & Quality → Energy Insights → Cost Estimate**. It is not connected to live grid equipment and does not operate appliances.

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run views/app.py
```

## Meter data workflow

In **Data & Quality**, upload a CSV or Excel `.xlsx` workbook, select a worksheet if needed, and map the timestamp, building/site, energy-in-kWh, and optional meter-ID fields. Invalid timestamps and negative or non-numeric readings are reported and excluded from the analysis. Missing building labels remain as `Unassigned`; duplicate meter-time records are reported but retained so the user can check their source.

**Energy Insights** compares total and daily kWh by building and highlights peak days/readings for investigation. A high reading is not automatically a fault. **Cost Estimate** applies the included illustrative progressive tariff to the selected building and period. The calculation treats that period as one billing cycle and one connection; it is not an official utility bill. Replace the example rates with a verified applicable tariff before making real decisions.

The bundled `data/sample_meter_readings.csv` is synthetic demonstration data, not actual campus readings. Load it only to preview the workflow. Use the CSV template or provide authorized meter data for a meaningful campus analysis.

## Sources and academic methods

**Sources** inspects public HTML tables separately as contextual data. Scraped content is not silently merged into campus meter totals. Respect website terms and access rules; the prototype does not bypass logins or paywalls and may not read JavaScript-rendered tables.

**Practical Lab** retains the programming exercises (billing/depreciation/series, queues/sets/topology, matrix operations, and general CSV/Excel analysis) for coursework. These are intentionally separate from the campus-energy product workflow where an exercise has no direct operational role.

## Limits

This project is for education and demonstration, not engineering, billing, safety, or operational advice. Dataset interpretations depend on source quality, mapped fields, units, and the selected assumptions. Do not upload confidential data to an unreviewed deployment.
