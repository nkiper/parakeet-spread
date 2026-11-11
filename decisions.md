# Decision log

Choices and their reasons. Limitations, to-dos and future work are in [`notes.md`](notes.md).

## Data

### 2026-11-10: Two sources
**Decision:** Use parakeet records from both GBIF and the NBN Atlas.
**Reason:** GBIF has a citable DOI and app data (eBird, iNaturalist); the NBN Atlas is the main UK database, mostly BTO data. They overlap very little, so either alone would miss much of the data.
- **GBIF:** *Psittacula krameri*, United Kingdom, has coordinates, no geospatial issues; simple format; 192,792 records; https://doi.org/10.15468/dl.xnh55x
- **NBN Atlas:** *Psittacula krameri* occurrence records; full Darwin Core; 243,105 records (CC-BY-NC: credit the data partners). Downloaded again on 11 Nov 2026 with identical records.
- Raw downloads are kept out of Git; they can be downloaded again.

### 2026-11-11: Merging
**Decision:** All NBN records, plus the GBIF records not already in NBN. Records in both are matched on GBIF `occurrenceID` = NBN `recordID` (checked on the Suffolk dataset); the NBN version is kept, because it has grid references and verification status.
**Result:** 1,727 records in both; 434,039 merged. GBIF records use `gbifID` as ID (36 have no `occurrenceID`).
**Not handled:** the same sighting entered separately in two systems (e.g. eBird and BirdTrack) has unrelated IDs. This does not affect presence per square and year.

### 2026-11-11: Filters
**Result:** 433,993 records kept.

| Filter | Removed | Reason |
|---|---|---|
| GBIF `NOT_DETECTED` (before merging) | 131 | Absence records |
| Vitality "dead" | 23 | Only "dead" is evidence against a live bird. "Not recorded" and empty are kept: GBIF has no vitality field, and whole NBN datasets never fill it in |
| No year | 18 | Needed for a yearly analysis |
| Before 1963 | 2 | Two isolated records from 1900; the next is from 1963 |
| Isle of Man | 3 | Not part of the UK, and not in the GBIF download |
| GBIF data-quality flags | 0 | Checked: years and locations are plausible |

## Spatial unit

### 2026-11-11: 10 km squares
**Decision:** 10 km squares on the British National Grid; 2 km squares only as a comparison from 1992.
**Reason:** Many early records have only 10 km resolution (largely BTO atlases), and finer squares would drop them. Most GBIF records have no coordinate uncertainty and 54% come from birding hotspots. Every record fits a 10 km square.

## Range and spread rate

### 2026-11-11: √(occupied area) per year
**Decision:** Range = number of occupied 10 km squares × 100 km² per year. Spread rate = slope of √(area) against year (Skellam 1951), reported as a radial rate (slope ÷ √π, since radius = √(area/π)). Fitted for two phases, 1970–2009 and 2010–2025.
**Reason:** For a population spreading at a constant rate, √(area) rises in a straight line. The plot shows a roughly constant slope until 2009 and a steeper one from 2010; 2010 is also when coverage becomes almost complete.
**Notes:**
- The phases are set from the plot, not estimated. The later rate depends on the boundary (from 2005: 3.1 km/yr; from 2013: 4.5 km/yr).
- The atlas start years (1968, 1981, 1988) are left out of the fits: the NBN Atlas dates each multi-year BTO atlas to its first year.

## Recording effort

### 2026-11-11: Benchmark species
**Decision:** A 10 km square counts as visited in a year if any of four benchmark species was recorded there: Wren, Robin, Blackbird, Blue Tit. Range index = share of visited squares with a parakeet record. Corrected area = index × 2,843 GB land squares × 100 km². Presence only, never record counts.
**Reason:** These species occur in almost every 10 km square and their range is stable, so their records show where people recorded, in the same unit as the parakeet range.
**Area:** Great Britain only. Irish Grid squares don't line up with British ones, and Northern Ireland has only ~65 parakeet records.

### 2026-11-11: Benchmark data
- **GBIF:** the four species, same filters as the parakeet download, years 1960–2026; simple format; 6,594,769 records; https://doi.org/10.15468/dl.4yeq82
- **NBN Atlas:** squares per species and year from the search API (`grid_ref_10000`), queried on 11 Nov 2026, instead of a ~26 GB download. Tested on the parakeet: the API squares match the downloaded data.

### 2026-11-11: NBN parakeet squares from the API too
**Finding:** The NBN Atlas download and API serve different versions of the BTO data (API ~255,900 parakeet records, download 243,105, the same on 10 and 11 Nov).
**Decision:** For the index, the NBN parakeet squares come from the API as well, so parakeet and visited squares come from the same NBN version. `records.parquet` remains the source for the maps and the uncorrected range in `03_yearly-range`.
**Reason:** Otherwise squares with parakeets only in the newer data would count as "visited, no parakeets", making the recent index ~5% too low.

### 2026-11-11: Results and limitations
**Spread rate (effort-corrected, radial, ± 2 SE):** 1970–2009: 1.68 ± 0.14 km/yr; 2010–2025: 4.03 ± 0.44 km/yr. The standard errors are too small, because consecutive years are not independent.
**What the correction does:** it corrects coverage. Before 1990 only 800–1,400 of 2,843 squares were visited per year, and the correction roughly doubles the area. From about 2008 nearly all squares are visited, and the correction has little effect.
**What it doesn't do:** it doesn't correct intensity (how thoroughly squares were visited). The atlas years still stand out, and the eBird growth after 2010 is not removed.
**Is the acceleration real?**

| Variant | 1970–2009 | 2010–2025 |
|---|---|---|
| Main index | 1.68 km/yr | 4.03 km/yr |
| NBN only (no eBird) | 1.74 km/yr | 3.39 km/yr |
| Persistent squares only (parakeets also the year before or after) | 1.37 km/yr | 4.03 km/yr |

**Conclusion:** Yes. The acceleration holds in both checks; eBird adds about 0.6 km/yr to the recent rate. NBN still contains BirdTrack, which also grew, so not all recording growth is removed.

## Open

- Origin of the spread: future work, building on Heald et al. (2019).
