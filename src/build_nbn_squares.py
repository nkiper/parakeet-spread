"""Collect 10 km squares per species and year from the NBN Atlas search API.

For each species and year, asks the NBN Atlas API how many records there are per 10 km
grid reference (facet on `grid_ref_10000`), so no records need to be downloaded.
Used for the benchmark species (recording effort) and for the parakeet (as a check
against the downloaded parakeet data). See decisions.md: "Benchmark data from NBN
Atlas: API instead of a download".

- British and Irish grid references are converted to British National Grid square
  IDs ('530_180'), the same as for the parakeet records.
- Squares on the Isle of Man are removed (decisions.md: "Isle of Man").
- The result is saved with the query date, because NBN data keeps changing. Run this
  on the same day as the NBN parakeet download.

Output: data/processed/nbn_squares_api.csv.gz
    one row per species, year and 10 km square, with the number of records
    (kept for checks only; the analysis uses presence, never counts)

Run from the project root (about 320 queries, a few minutes):
    python src/build_nbn_squares.py
"""

import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from shapely.geometry import box

from grid import hectad_from_any_gridref, load_countries
from pipeline import FIRST_YEAR

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
LAND_PATH = ROOT / "data" / "external" / "ne_10m_admin_0_countries.zip"
OUT_PATH = PROCESSED / "nbn_squares_api.csv.gz"

API_URL = "https://records-ws.nbnatlas.org/occurrences/search"
GRID_FIELD = "grid_ref_10000"
FACET_LIMIT = 10_000  # far more than the number of 10 km squares in the UK
LAST_YEAR = 2026      # 2026 is collected but excluded from the analysis (incomplete year)

SPECIES = {
    "Ring-necked Parakeet": "Psittacula krameri",  # check against the downloaded parakeet data
    "Wren": "Troglodytes troglodytes",
    "Robin": "Erithacus rubecula",
    "Blackbird": "Turdus merula",
    "Blue Tit": "Cyanistes caeruleus",
}


def query_squares(name: str, year: int, attempts: int = 3) -> dict:
    """Number of NBN records per 10 km grid reference for one species and year."""
    params = {"q": f'taxon_name:"{name}"', "fq": f"year:{year}",
              "facets": GRID_FIELD, "flimit": FACET_LIMIT, "pageSize": 0}
    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(API_URL, params=params, timeout=120)
            r.raise_for_status()
            break
        except requests.RequestException as err:
            if attempt == attempts:
                raise
            print(f"    retry {attempt} for {name} {year}: {err}")
            time.sleep(5 * attempt)

    results = r.json().get("facetResults") or []
    field = next((f for f in results if f.get("fieldName") == GRID_FIELD), {"fieldResult": []})
    counts = {f["label"]: f["count"] for f in field["fieldResult"]}
    assert len(counts) < FACET_LIMIT, f"facet limit reached for {name} {year}"
    return counts


def isle_of_man_squares(hectads) -> set:
    """The 10 km squares (from `hectads`) that overlap the Isle of Man."""
    countries = load_countries(LAND_PATH)
    iom = countries[countries["ADM0_A3"] == "IMN"].to_crs("EPSG:27700").geometry.union_all()
    iom_squares = set()
    for hectad in hectads:
        e_km, n_km = map(int, hectad.split("_"))
        if box(e_km * 1000, n_km * 1000, (e_km + 10) * 1000, (n_km + 10) * 1000).intersects(iom):
            iom_squares.add(hectad)
    return iom_squares


def main():
    query_date = date.today().isoformat()
    years = range(FIRST_YEAR, LAST_YEAR + 1)
    rows = []
    for label, name in SPECIES.items():
        print(f"{label} ({name})")
        for year in years:
            for gridref, n in query_squares(name, year).items():
                rows.append({"species": label, "year": year, "gridref": gridref, "n_records": n})
            time.sleep(0.2)  # be polite to the API
        print(f"  {sum(r['species'] == label for r in rows):,} species-year-gridref rows")

    squares = pd.DataFrame(rows)
    squares["hectad"] = squares["gridref"].map(hectad_from_any_gridref)

    unparsed = squares["hectad"].isna()
    if unparsed.any():
        print(f"Grid references that are neither British nor Irish (dropped): "
              f"{sorted(squares.loc[unparsed, 'gridref'].unique())[:20]}")
    squares = squares[~unparsed]

    iom = isle_of_man_squares(squares["hectad"].unique())
    is_iom = squares["hectad"].isin(iom)
    print(f"Isle of Man squares removed: {len(iom)} squares, {is_iom.sum():,} rows")
    squares = squares[~is_iom]

    # Two grid references can map to the same square (e.g. near the Irish/British grid
    # boundary); combine them so there is one row per species, year and square.
    squares = (squares.groupby(["species", "year", "hectad"], as_index=False)
                      .agg(n_records=("n_records", "sum"), gridref=("gridref", "first")))
    squares["query_date"] = query_date

    PROCESSED.mkdir(parents=True, exist_ok=True)
    squares.to_csv(OUT_PATH, index=False)
    print(f"Saved {len(squares):,} rows to {OUT_PATH.relative_to(ROOT)} (query date {query_date})")
    print(squares.groupby("species")["hectad"].nunique().rename("squares (all years)").to_string())


if __name__ == "__main__":
    main()
