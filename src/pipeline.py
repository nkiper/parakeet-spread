"""Cleaning steps shared by the parakeet and benchmark pipelines.

Used by build_records.py (parakeets) and build_gbif_benchmarks.py (benchmark species),
so both are cleaned in exactly the same way. Each step refers to its entry in
decisions.md.

The functions work on a table with at least these columns: year, decimalLatitude,
decimalLongitude, vitality, countryCode (GBIF records: vitality empty, countryCode "GB").
"""

from collections import Counter

import geopandas as gpd
import numpy as np
import pandas as pd

from grid import square_id

FIRST_YEAR = 1963  # decisions.md: "Year filters"


def _report(removed, label, n):
    """Print a removal count, or add it to `removed` (a Counter) when processing in chunks."""
    if removed is None:
        print(f"  removed {n:,} {label}")
    else:
        removed[label] += n


def _equals(column: pd.Series, value: str) -> pd.Series:
    """True where `column` equals `value`; missing values count as not equal."""
    return column.eq(value).fillna(False).astype(bool)


def drop_absences(gbif: pd.DataFrame, removed: Counter | None = None) -> pd.DataFrame:
    """Keep only GBIF records where the species was detected.

    decisions.md: "GBIF absence records".
    """
    keep = gbif["occurrenceStatus"] == "DETECTED"
    _report(removed, "NOT_DETECTED records", int((~keep).sum()))
    return gbif[keep]


def apply_filters(records: pd.DataFrame, removed: Counter | None = None) -> pd.DataFrame:
    """Apply the record filters. Prints how many records each removes, or adds the
    counts to `removed` when processing in chunks."""

    def drop(mask_keep, label):
        nonlocal records
        _report(removed, label, int((~mask_keep).sum()))
        records = records[mask_keep]

    if removed is None:
        print("Filters:")
    # decisions.md: "Vitality filter" (keep alive, not recorded and empty)
    drop(~_equals(records["vitality"], "dead"), "dead records")
    # decisions.md: "Year filters"
    drop(records["year"].notna(), "records without a year")
    drop(records["year"] >= FIRST_YEAR, f"records before {FIRST_YEAR}")
    # decisions.md: "Isle of Man"
    drop(~_equals(records["countryCode"], "IM"), "Isle of Man records")
    # decisions.md: "GBIF data-quality flags": all flagged records are kept, no filter.

    return records.reset_index(drop=True)


def add_squares(records: pd.DataFrame, quiet: bool = False) -> pd.DataFrame:
    """Add British National Grid coordinates and 10 km / 2 km square IDs.

    decisions.md: "Spatial unit". Northern Ireland records are placed on the British
    National Grid too, so all records use the same squares.
    """
    points = gpd.points_from_xy(
        records["decimalLongitude"], records["decimalLatitude"], crs="EPSG:4326"
    ).to_crs("EPSG:27700")
    records = records.assign(easting=points.x, northing=points.y)
    assert np.isfinite(records[["easting", "northing"]]).all().all(), "coordinate conversion failed"

    records["hectad"] = square_id(records["easting"], records["northing"], 10_000)  # 10 km
    records["tetrad"] = square_id(records["easting"], records["northing"], 2_000)   # 2 km
    if not quiet:
        print(f"Squares: {records['hectad'].nunique():,} occupied 10 km, "
              f"{records['tetrad'].nunique():,} occupied 2 km")
    return records
