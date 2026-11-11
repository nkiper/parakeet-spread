"""Build the merged and filtered parakeet records table.

Loads the raw GBIF and NBN Atlas downloads, merges them into one table and applies
the filters decided in notebooks/01_explore-sources.ipynb. Each step refers to its
entry in decisions.md.

Output: data/processed/records.parquet

Run from the project root:
    python src/build_records.py
"""

from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

GBIF_PATH = RAW / "0000595-261110092616502.csv"
NBN_PATH = RAW / "records-2026-11-10" / "records-2026-11-10.csv"
DATASETS_PATH = PROCESSED / "gbif_datasets.csv"  # cached GBIF dataset titles
OUT_PATH = PROCESSED / "records.parquet"

GBIF_COLS = [
    "gbifID", "datasetKey", "occurrenceID",
    "eventDate", "year", "month",
    "decimalLatitude", "decimalLongitude", "coordinateUncertaintyInMeters",
    "stateProvince",
    "scientificName", "taxonRank", "occurrenceStatus", "issue",
    "institutionCode", "collectionCode", "catalogNumber", "individualCount",
]

NBN_COLS = [
    "recordID", "occurrenceID",
    "eventDate", "year", "month", "startDayOfYear", "endDayOfYear",
    "decimalLatitude", "decimalLongitude", "coordinateUncertaintyInMeters",
    "gridReference", "stateProvince", "countryCode",
    "identificationVerificationStatus", "vitality",
    "datasetName", "institutionCode", "collectionCode", "individualCount",
]

FIRST_YEAR = 1963  # decisions.md: "Year filters"


# --- Loading -----------------------------------------------------------------

def load_gbif() -> pd.DataFrame:
    """Load the GBIF simple download and remove absence records."""
    gbif = pd.read_csv(
        GBIF_PATH,
        sep="\t",    # simple downloads are tab-separated despite the .csv extension
        quoting=3,   # csv.QUOTE_NONE, recommended by GBIF
        usecols=GBIF_COLS,
        dtype={"gbifID": str, "occurrenceID": str, "catalogNumber": str},
    )
    print(f"GBIF loaded: {len(gbif):,}")

    # decisions.md: "GBIF absence records"
    before = len(gbif)
    gbif = gbif[gbif["occurrenceStatus"] == "DETECTED"]
    print(f"  removed {before - len(gbif):,} NOT_DETECTED records")
    return gbif


def load_nbn() -> pd.DataFrame:
    """Load the NBN Atlas download (full Darwin Core)."""
    nbn = pd.read_csv(
        NBN_PATH,
        usecols=NBN_COLS,
        dtype={"recordID": str, "occurrenceID": str, "gridReference": str},
        parse_dates=["eventDate"],  # empty (NaT) for records with only year and month
    )
    print(f"NBN loaded: {len(nbn):,}")
    return nbn


def load_dataset_titles(dataset_keys) -> pd.Series:
    """Return GBIF dataset titles by datasetKey.

    Titles are looked up with the GBIF API once and cached in DATASETS_PATH, so
    later runs work offline and give the same result. Delete the file to refresh it.
    """
    if DATASETS_PATH.exists():
        cached = pd.read_csv(DATASETS_PATH)
        missing = set(dataset_keys) - set(cached["datasetKey"])
        if not missing:
            return cached.set_index("datasetKey")["title"]
        print(f"  {len(missing)} datasets missing from cache, refreshing")

    rows = []
    for key in sorted(set(dataset_keys)):
        d = requests.get(f"https://api.gbif.org/v1/dataset/{key}", timeout=30).json()
        org = requests.get(
            f"https://api.gbif.org/v1/organization/{d['publishingOrganizationKey']}",
            timeout=30,
        ).json()
        rows.append({"datasetKey": key, "title": d.get("title"), "publisher": org.get("title")})

    meta = pd.DataFrame(rows)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    meta.to_csv(DATASETS_PATH, index=False)
    print(f"  saved {len(meta)} dataset titles to {DATASETS_PATH.relative_to(ROOT)}")
    return meta.set_index("datasetKey")["title"]


# --- Merging -----------------------------------------------------------------

def merge(gbif: pd.DataFrame, nbn: pd.DataFrame) -> pd.DataFrame:
    """All NBN records plus the GBIF records not already in NBN.

    decisions.md: "Matching records between GBIF and NBN Atlas" and
    "Merging GBIF and NBN Atlas". For NBN-hosted datasets, GBIF occurrenceID = NBN
    recordID; for records in both, the NBN version is kept.
    """
    in_nbn = gbif["occurrenceID"].isin(set(nbn["recordID"]))
    gbif_only = gbif[~in_nbn]
    print(f"GBIF records also in NBN: {in_nbn.sum():,} | GBIF-only: {len(gbif_only):,}")

    # eventDate: keep only full dates (YYYY-MM-DD), like NBN. Year-only, year-month
    # and date ranges ("2020-05-01/2020-05-31") become NaT, so no day is made up.
    gbif_date = (
        gbif_only["eventDate"]
        .where(~gbif_only["eventDate"].str.contains("/", na=False))
        .str[:10]  # drops times, e.g. "2021-04-03T10:15" -> "2021-04-03"
    )
    dataset_titles = load_dataset_titles(gbif["datasetKey"].unique())

    gbif_std = pd.DataFrame({
        "source": "GBIF",
        "record_id": gbif_only["gbifID"],          # always filled; some records have no occurrenceID
        "occurrenceID": gbif_only["occurrenceID"],
        "dataset": gbif_only["datasetKey"].map(dataset_titles),
        "eventDate": pd.to_datetime(gbif_date, format="%Y-%m-%d", errors="coerce"),
        "year": gbif_only["year"].astype("Int64"),  # Int64 allows missing values
        "month": gbif_only["month"].astype("Int64"),
        "decimalLatitude": gbif_only["decimalLatitude"],
        "decimalLongitude": gbif_only["decimalLongitude"],
        "coordinateUncertaintyInMeters": gbif_only["coordinateUncertaintyInMeters"],
        "gridReference": pd.NA,                     # not in the GBIF simple format
        "stateProvince": gbif_only["stateProvince"].str.split(" - ").str[0],  # "England - Kent" -> "England"
        "individualCount": gbif_only["individualCount"],
        "vitality": pd.NA,                          # not in the GBIF simple format
        "countryCode": "GB",                        # the GBIF query was filtered on United Kingdom
        "issue": gbif_only["issue"],
    })

    nbn_std = pd.DataFrame({
        "source": "NBN",
        "record_id": nbn["recordID"],
        "occurrenceID": nbn["recordID"],            # the ID GBIF uses for NBN records
        "dataset": nbn["datasetName"],
        "eventDate": nbn["eventDate"],
        "year": nbn["year"].astype("Int64"),
        "month": nbn["month"].astype("Int64"),
        "decimalLatitude": nbn["decimalLatitude"],
        "decimalLongitude": nbn["decimalLongitude"],
        "coordinateUncertaintyInMeters": nbn["coordinateUncertaintyInMeters"],
        "gridReference": nbn["gridReference"],
        "stateProvince": nbn["stateProvince"],
        "individualCount": nbn["individualCount"],
        "vitality": nbn["vitality"].str.lower(),    # "Alive" and "alive" -> "alive"
        "countryCode": nbn["countryCode"],
        "issue": pd.NA,                             # GBIF-only field
    })

    records = pd.concat([nbn_std, gbif_std], ignore_index=True)

    assert len(records) == len(nbn) + len(gbif_only), "records lost or doubled in merge"
    assert records["record_id"].is_unique, "record_id is not unique"
    print(f"Merged: {len(records):,}")
    return records


# --- Filtering ---------------------------------------------------------------

def apply_filters(records: pd.DataFrame) -> pd.DataFrame:
    """Apply the record filters, printing how many records each one removes."""

    def drop(mask_keep, label):
        nonlocal records
        before = len(records)
        records = records[mask_keep]
        print(f"  removed {before - len(records):,} {label}")

    print("Filters:")
    # decisions.md: "Vitality filter" (keep alive, not recorded and empty)
    drop(records["vitality"] != "dead", "dead records")
    # decisions.md: "Year filters"
    drop(records["year"].notna(), "records without a year")
    drop(records["year"] >= FIRST_YEAR, f"records before {FIRST_YEAR}")
    # decisions.md: "Isle of Man"
    drop(records["countryCode"] != "IM", "Isle of Man records")
    # decisions.md: "GBIF data-quality flags": all flagged records are kept, no filter.

    return records.reset_index(drop=True)


# --- Main --------------------------------------------------------------------

def main():
    gbif = load_gbif()
    nbn = load_nbn()
    records = merge(gbif, nbn)
    records = apply_filters(records)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    records.to_parquet(OUT_PATH, index=False)
    print(f"Saved {len(records):,} records to {OUT_PATH.relative_to(ROOT)}")
    print(records["source"].value_counts().to_string())


if __name__ == "__main__":
    main()
