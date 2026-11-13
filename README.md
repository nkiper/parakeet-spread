# Spread of ring-necked parakeets in the UK

How fast the ring-necked parakeet (*Psittacula krameri*), an introduced species, has spread across Great Britain, using open occurrence records from GBIF and the NBN Atlas.

## Result

Corrected for recording effort, the parakeet's range spread at about **1.6 km per year from 1970 to 2009** and **3.4–4 km per year from 2010 to 2025**. The acceleration holds without eBird data and with persistently occupied squares only, so it is not just more birdwatching. The correction covers where people recorded, not how intensively, so up to about 0.6 km/yr of the recent rate may still be recording growth.

The BTO atlases, left out of the fits, are an independent check: the 1968–72 and 1988–91 breeding atlases lie on the 1970–2009 trend line. The 1981–84 Winter Atlas lies above it, as do the other records from those winters.

**Why the spread accelerated:** a simple model following Skellam (1951) has circles spreading at one constant speed from six centres, the largest separate clusters on the 2025 map (London, Manchester, Birmingham, Newcastle, Nottingham, Glasgow), with speed and start years fitted to the 1970–2025 range curve. At 1.5 km/yr it fits much better than London alone (RMSE 8.1 against 15.2 km of √area). As new centres start, the model's own spread rate rises from 1.7 to 3.1 km/yr: about 60% of the observed speed-up (1.6 → 4.0). Windows that span the stall after Bird Atlas 2007–11 (from 2005 or 2007) give 72–80%. The result holds with persistently occupied squares only. London starts first, the others between about 1990 and the mid-2000s, but their exact start years are poorly determined. About half of the squares occupied in 2025 lie outside all six circles; Cardiff, despite early records, stayed in the coastal urban belt and is not a centre.

Figures are in `figures/` (animation: `hectads_by_year.mp4`). Choices and their reasons are in [`decisions.md`](decisions.md); limitations, to-dos and future work in [`notes.md`](notes.md).

**Status:** analysis complete; presentation in progress.

## Method

1. Merge and clean the GBIF and NBN Atlas records (`01_explore-sources`, `src/build_records.py`).
2. Assign records to 10 km British National Grid squares (`02_spatial-unit`).
3. Occupied area per year; spread rate as the slope of √(area) against year, following Skellam (1951) (`03_yearly-range`).
4. Correct for recording effort with four common bird species as benchmarks for which squares were visited; spread rates, robustness checks, and the BTO atlases as an independent check (`04_effort-correction`).
5. Spread model: circles growing at one constant speed from six centres chosen from the 2025 map; speed and start years fitted to the 1970–2025 range curve, compared with a London-only model and with the maps; why Cardiff is not a centre (`05_spread-model`).

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
data/processed/   built tables: records, benchmark squares, range index, spread rates, atlas check, spread model fits
data/external/    land outlines (downloaded automatically, not tracked)
src/              build scripts; shared steps in pipeline.py and grid.py; plot_style.py (fonts,
                  colours); skellam_animation.py (Skellam animations for the talk)
notebooks/        analysis, 01–05
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
