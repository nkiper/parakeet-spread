"""British National Grid helpers shared by the scripts and notebooks.

Square IDs are the south-west corner of the square in km, e.g. '530_180' for the
10 km square from 530-540 km east and 180-190 km north.
"""

import re
from pathlib import Path

import requests
from pyproj import Transformer

_GRIDREF = re.compile(r"([A-HJ-Z]{2})(\d+)[A-NP-Z]?")        # British: two letters (no I), digits
_IRISH_GRIDREF = re.compile(r"([A-HJ-Z])(\d+)[A-NP-Z]?")     # Irish: one letter (no I), digits
_LETTERS = "ABCDEFGHJKLMNOPQRSTUVWXYZ"                        # grid letters skip I

# Irish Grid (TM75) -> British National Grid
_IRISH_TO_BNG = Transformer.from_crs("EPSG:29903", "EPSG:27700", always_xy=True)

LAND_URL = "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip"


def square_id(easting, northing, size_m):
    """ID of the grid square containing each point (pandas Series of eastings/northings in metres)."""
    e_km = (easting // size_m * size_m / 1000).astype(int)
    n_km = (northing // size_m * size_m / 1000).astype(int)
    return e_km.astype(str) + "_" + n_km.astype(str)


def hectad_from_gridref(ref):
    """10 km square ID ('530_170') from a British OS grid reference like 'TQ37' or 'TQ2464', or None.

    Irish Grid references (one letter, used in Northern Ireland) return None.
    """
    m = _GRIDREF.fullmatch(ref) if isinstance(ref, str) else None
    if m is None or len(m.group(2)) % 2:
        return None
    l1, l2 = _LETTERS.index(m.group(1)[0]), _LETTERS.index(m.group(1)[1])
    e100 = ((l1 - 2) % 5) * 5 + (l2 % 5)        # 100 km square, easting
    n100 = (19 - (l1 // 5) * 5) - (l2 // 5)     # 100 km square, northing
    digits = m.group(2)
    half = len(digits) // 2
    e_km = e100 * 100 + int(digits[0]) * 10       # first digit of each half = 10 km square
    n_km = n100 * 100 + int(digits[half]) * 10
    return f"{e_km}_{n_km}"


def hectad_from_irish_gridref(ref):
    """British National Grid 10 km square ID for an Irish Grid reference like 'J37', or None.

    The centre of the Irish 10 km square is converted to the British National Grid,
    so Northern Ireland records end up in the same squares as when their coordinates
    are converted (decisions.md: "Spatial unit").
    """
    m = _IRISH_GRIDREF.fullmatch(ref) if isinstance(ref, str) else None
    if m is None or len(m.group(2)) % 2:
        return None
    idx = _LETTERS.index(m.group(1))
    e100, n100 = idx % 5, 4 - idx // 5             # 5 x 5 grid of 100 km squares, A at top left
    digits = m.group(2)
    half = len(digits) // 2
    e_centre = (e100 * 100 + int(digits[0]) * 10 + 5) * 1000      # metres, centre of the 10 km square
    n_centre = (n100 * 100 + int(digits[half]) * 10 + 5) * 1000
    e, n = _IRISH_TO_BNG.transform(e_centre, n_centre)
    return f"{int(e // 10_000 * 10)}_{int(n // 10_000 * 10)}"


def hectad_from_any_gridref(ref):
    """10 km square ID from a British or Irish grid reference, or None if neither."""
    return hectad_from_gridref(ref) or hectad_from_irish_gridref(ref)


def gb_land_hectads(countries, buffer_m: float = 1000) -> set:
    """IDs of all 10 km squares that touch Great Britain (UK without Northern Ireland).

    `countries` is the Natural Earth table from `load_countries`. Northern Ireland is
    the part of the UK outline that touches Ireland. A small buffer (`buffer_m`) keeps
    coastal squares whose land is missed by the generalised coastline.
    """
    import geopandas as gpd
    import numpy as np
    from shapely import box as boxes
    from shapely.ops import unary_union

    uk = countries.loc[countries["ADM0_A3"] == "GBR"].to_crs("EPSG:27700").geometry.union_all()
    ireland = countries.loc[countries["ADM0_A3"] == "IRL"].to_crs("EPSG:27700").geometry.union_all()
    near_ireland = ireland.buffer(100)
    gb = unary_union([part for part in uk.geoms if not part.intersects(near_ireland)]).buffer(buffer_m)

    xmin, ymin, xmax, ymax = gb.bounds
    e = np.arange(xmin // 10_000 * 10_000, xmax + 10_000, 10_000)
    n = np.arange(ymin // 10_000 * 10_000, ymax + 10_000, 10_000)
    ee, nn = (a.ravel() for a in np.meshgrid(e, n))
    squares = gpd.GeoSeries(boxes(ee, nn, ee + 10_000, nn + 10_000), crs="EPSG:27700")
    touches = squares.intersects(gb).to_numpy()
    return {f"{int(x // 1000)}_{int(y // 1000)}" for x, y in zip(ee[touches], nn[touches])}


def load_countries(path: Path):
    """Natural Earth country outlines (public domain), downloaded to `path` if missing."""
    import geopandas as gpd  # imported here so the grid-reference helpers don't need geopandas

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(requests.get(LAND_URL, timeout=60).content)
    return gpd.read_file(path)
