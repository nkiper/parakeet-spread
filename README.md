# Spread of ring-necked parakeets in the UK

Mapping how the ring-necked parakeet (*Psittacula krameri*), an introduced species, has spread across the UK over time, using open occurrence records.

## Status

Work in progress. Sources compared and merged into one table; data cleaning is next.

- [x] Project setup
- [x] Download records from GBIF and the NBN Atlas
- [x] Compare sources: records per year, overlap, data quality (`01_explore-sources`)
- [x] Choose main source: merged (all NBN records plus GBIF-only records)
- [ ] Clean data: filters (e.g. vitality, coordinate uncertainty) and duplicate sightings across sources
- [ ] Choose spatial unit and yearly range metric
- [ ] Correct for recording effort
- [ ] Map and quantify the spread

Methodological choices and their reasons are logged in [`decisions.md`](decisions.md).

## Data

Downloaded on 10 November 2026:

| Source | Query | Format | Records |
|---|---|---|---|
| GBIF | *P. krameri*, United Kingdom, with coordinates, no geospatial issues | Simple | 192,792 |
| NBN Atlas | *P. krameri*, occurrence records | Full Darwin Core | 243,105 |

Raw data is not tracked in Git. To reproduce, download from the GBIF DOI below and rerun the NBN Atlas query, then place both files in `data/raw/`.

## Structure

```
data/raw/         original downloads (not tracked)
data/processed/   merged and filtered records (records.parquet, not tracked) and GBIF dataset titles
src/              scripts (build_records.py: merge, filter and save the records)
docs/             relevant papers
notebooks/        analysis notebooks
figures/          maps and plots
decisions.md      decision log
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Place the raw downloads in `data/raw/`:

- GBIF: `data/raw/0000595-261110092616502.csv`
- NBN Atlas: unzip to `data/raw/records-2026-11-10/`

Then build the merged and filtered records table:

```bash
python src/build_records.py
```

This writes `data/processed/records.parquet`, which the analysis notebooks after `01_explore-sources` start from.

## Data citation

- GBIF.org (10 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.xnh55x
- NBN Atlas occurrence download at NBN Atlas (https://nbnatlas.org/), accessed on 10 November 2026.

NBN Atlas records come from many data partners, under CC-BY-NC. Thanks to the NBN Atlas, its data partners, and all recorders.