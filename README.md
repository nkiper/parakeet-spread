# Spread of ring-necked parakeets in the UK

Mapping how the ring-necked parakeet (*Psittacula krameri*), an introduced species, has spread across the UK over time, using open occurrence records.

## Status

Work in progress. Data downloaded; exploration not yet started.

- [x] Project setup
- [x] Download records from GBIF and the NBN Atlas
- [ ] Compare sources: records per year, overlap, data quality (`01_explore_sources`)
- [ ] Choose main source and clean data
- [ ] Choose spatial unit and yearly range metric
- [ ] Correct for recording effort
- [ ] Map and quantify the spread

Methodological choices and their reasons are logged in [`decisions.md`](decisions.md).

## Data

Downloaded on 10 November 2026:

| Source | Query | Format | Records |
|---|---|---|---|
| GBIF | *P. krameri*, United Kingdom, with coordinates, no geospatial issues | Simple | 192,792 |
| NBN Atlas | *P. krameri*, occurrence records | Full Darwin Core | 232,722 |

Raw data is not tracked in Git. To reproduce, download from the GBIF DOI below and rerun the NBN Atlas query, then place both files in `data/raw/`.

## Structure

data/raw/ original downloads (not tracked)
data/processed/ cleaned data
docs/ relevant papers
notebooks/ analysis notebooks
figures/ maps and plots
decisions.md decision log


## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Data citation

- GBIF.org (10 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.xnh55x
- NBN Atlas occurrence download at NBN Atlas (https://nbnatlas.org/), accessed on 10 November 2026.

NBN Atlas records come from many data partners, under CC-BY-NC. Thanks to the NBN Atlas, its data partners, and all recorders.