"""Build the 10 km squares per species and year for the benchmark species from GBIF.

Reads the GBIF benchmark download (simple format, several GB) in chunks, applies the
same cleaning as the parakeet records (pipeline.py), assigns 10 km squares, and keeps
only one row per species, year and square. See decisions.md: "Recording effort:
benchmark species" and "Benchmark data from GBIF".

The GBIF-NBN overlap step of the parakeet pipeline is not needed here: a record that
is in both sources marks the same square in the same year, so it cannot change
presence per square and year.

Output: data/processed/gbif_benchmark_squares.csv.gz
    one row per species, year and 10 km square, with the number of records
    (kept for checks only; the analysis uses presence, never counts)

Run from the project root:
    python src/build_gbif_benchmarks.py data/raw/benchmarks/<download>.csv
"""

import sys
from collections import Counter
from pathlib import Path

import pandas as pd

from pipeline import add_squares, apply_filters, drop_absences

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUT_PATH = PROCESSED / "gbif_benchmark_squares.csv.gz"

CHUNK_SIZE = 1_000_000
COLUMNS = ["species", "year", "decimalLatitude", "decimalLongitude", "occurrenceStatus", "countryCode"]

SPECIES = {
    "Troglodytes troglodytes": "Wren",
    "Erithacus rubecula": "Robin",
    "Turdus merula": "Blackbird",
    "Cyanistes caeruleus": "Blue Tit",
}


def process_chunk(chunk: pd.DataFrame, removed: Counter) -> pd.DataFrame:
    """Clean one chunk and reduce it to records per species, year and 10 km square."""
    chunk = drop_absences(chunk, removed)

    other_species = ~chunk["species"].isin(SPECIES)
    removed["records of other species"] += int(other_species.sum())
    chunk = chunk[~other_species]

    chunk = chunk.assign(
        species=chunk["species"].map(SPECIES),
        year=chunk["year"].astype("Int64"),
        vitality=pd.NA,  # not in the GBIF simple format
    )
    chunk = apply_filters(chunk, removed)
    chunk = add_squares(chunk, quiet=True)
    return chunk.groupby(["species", "year", "hectad"]).size().rename("n_records").reset_index()


def main(path: Path):
    removed = Counter()
    n_read = 0
    parts = []
    reader = pd.read_csv(path, sep="\t", quoting=3, usecols=COLUMNS,
                         dtype={"species": str, "countryCode": str}, chunksize=CHUNK_SIZE)
    for i, chunk in enumerate(reader, start=1):
        n_read += len(chunk)
        parts.append(process_chunk(chunk, removed))
        print(f"  chunk {i}: {n_read:,} records read")

    squares = (pd.concat(parts)
                 .groupby(["species", "year", "hectad"], as_index=False)["n_records"].sum())

    print(f"GBIF benchmark records read: {n_read:,}")
    for label, n in removed.items():
        print(f"  removed {n:,} {label}")
    print(f"Records kept: {squares['n_records'].sum():,}")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    squares.to_csv(OUT_PATH, index=False)
    print(f"Saved {len(squares):,} rows to {OUT_PATH.relative_to(ROOT)}")
    print(squares.groupby("species")["hectad"].nunique().rename("squares (all years)").to_string())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python src/build_gbif_benchmarks.py data/raw/benchmarks/<download>.csv")
    main(Path(sys.argv[1]))
