# Spread of ring-necked parakeets in the UK

How fast the ring-necked parakeet (*Psittacula krameri*), an introduced species, has spread across Great Britain, using open occurrence records from GBIF and the NBN Atlas.

## Result

Corrected for recording effort, the parakeet's range spread at about **1.7 km per year from 1970 to 2009** and **3.4–4 km per year from 2010 to 2025**. The acceleration holds without eBird data and with persistently occupied squares only, so it is not just more birdwatching. The correction covers where people recorded, not how intensively, so up to about 0.6 km/yr of the recent rate may still be recording growth.

Figures are in `figures/` (animation: `hectads_by_year.mp4`). Choices and their reasons are in [`decisions.md`](decisions.md); limitations, to-dos and future work in [`notes.md`](notes.md).

**Status:** analysis complete; presentation in progress.

## Method

1. Merge and clean the GBIF and NBN Atlas records (`01_explore-sources`, `src/build_records.py`).
2. Assign records to 10 km British National Grid squares (`02_spatial-unit`).
3. Occupied area per year; spread rate as the slope of √(area) against year, following Skellam (1951) (`03_yearly-range`).
4. Correct for recording effort with four common bird species as benchmarks for which squares were visited; spread rates and robustness checks (`04_effort-correction`).

## Data

| Data | Source | Records |
|---|---|---|
| Parakeet | GBIF, 10 Nov 2026 ([DOI](https://doi.org/10.15468/dl.xnh55x)) | 192,792 |
| Parakeet | NBN Atlas download, 10 Nov 2026 (again 11 Nov, identical) | 243,105 |
| Benchmarks (Wren, Robin, Blackbird, Blue Tit) | GBIF, 11 Nov 2026 ([DOI](https://doi.org/10.15468/dl.4yeq82)) | 6,594,769 |
| Benchmarks and parakeet, squares per year | NBN Atlas API, 11 Nov 2026 | `data/processed/nbn_squares_api.csv.gz` |

Raw downloads are not in Git. The NBN Atlas API results can't be reproduced exactly later, so they are kept in Git.

## Reproduce

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Place the downloads in `data/raw/`: the GBIF parakeet file as `0000595-261110092616502.csv`, the NBN Atlas download unzipped to `records-2026-11-11/`, and the GBIF benchmark zip in `benchmarks/`. Then:

```bash
python src/build_records.py                 # parakeet records -> data/processed/records.parquet
python src/build_gbif_benchmarks.py data/raw/benchmarks/0002043-261110092616502.zip
python src/build_nbn_squares.py             # optional: refreshes the NBN Atlas API results
```

and run the notebooks in order.

## Structure

```
data/raw/         downloads (not tracked)
data/processed/   built tables: records, benchmark squares, range index, spread rates
data/external/    land outlines (downloaded automatically, not tracked)
src/              build scripts; shared steps in pipeline.py and grid.py
notebooks/        analysis, 01–04
figures/          maps and plots
docs/             papers
```

## Data citation

- GBIF.org (10 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.xnh55x
- GBIF.org (11 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.4yeq82
- NBN Atlas occurrence download at NBN Atlas (https://nbnatlas.org/), accessed on 10 November 2026.
- NBN Atlas occurrence records via the NBN Atlas API (https://records-ws.nbnatlas.org/), accessed on 11 November 2026.
- Land outlines: Natural Earth (public domain).

NBN Atlas records come from many data partners, under CC-BY-NC. Thanks to the NBN Atlas, its data partners, and all recorders.
