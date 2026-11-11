# Decision log

## 2026-11-10: Data sources
**Decision:** Download parakeet records from both GBIF and the NBN Atlas, then compare
them before choosing a main source.
**Reason:** GBIF gives a citable DOI and includes international sources (eBird,
iNaturalist). The NBN Atlas is the main UK database and may contain records not passed
on to GBIF. Comparing both first shows which is more complete.

## 2026-11-10: GBIF download
**Query:** (Scientific name = Psittacula krameri AND Country = United Kingdom AND Has coordinate = Yes AND Has geospatial issue = No)
**Taxonomic reference:** GBIF default (Catalogue of Life).
**Format:** Simple
**Records:** 192,792. Excluding geospatial issues removed 0 records.
**DOI:** https://doi.org/10.15468/dl.xnh55x
**Citation:** GBIF.org (10 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.xnh55x
**Reason:** Simple format has all fields needed (date, coordinates, uncertainty,
record type, dataset). Filtering on coordinates in the query; all other filtering done
in code.
**Download link:** https://api.gbif.org/v1/occurrence/download/request/0000595-261110092616502.zip

## 2026-11-10: NBN Atlas download
**Query:** Psittacula krameri, occurrence records.
**Format:** Full Darwin Core
**Records:** 243,105
**Reason:** Same column standard as GBIF, which makes comparison and duplicate
detection easier. Includes grid reference and verification status.
**Licence note:** Records come from many data partners under CC-BY-NC licence. Credit the NBN Atlas and data partners in README and slides.
**Citation:** NBN Atlas occurrence download at NBN Atlas [https://nbnatlas.org/] accessed on 10 November 2026.

## 2026-11-10: Raw data storage
**Decision:** Store raw downloads in data/raw/, excluded from Git via .gitignore.
**Reason:** Files are large. The data can be re-downloaded using the GBIF DOI and the
NBN query documented above.

## 2026-11-11: GBIF absence records
**Decision:** Remove GBIF records with `occurrenceStatus` = NOT_DETECTED.
**Records:** 131 removed, 192,661 kept.
**Reason:** These record that a parakeet was looked for and not found. They do not
show where the species occurs.

## 2026-11-11: Matching records between GBIF and NBN Atlas
**Decision:** Use GBIF `occurrenceID` = NBN `recordID` as the exact match key for
records present in both sources.
**Reason:** For NBN-hosted datasets, GBIF stores the NBN record UUID in `occurrenceID`.
Checked on the Suffolk (SBIS) dataset: same ID, same date and same coordinates in both
sources. NBN's own `occurrenceID` is the data provider's internal code (e.g.
`WA0000050000AZZY`) and does not match GBIF.
**Note:** This only finds records passed from NBN to GBIF. The same sighting entered
separately in two systems (e.g. eBird and BirdTrack) has unrelated IDs and needs a
content-based check (same date and grid square).

## 2026-11-11: Merging GBIF and NBN Atlas
**Decision:** Use both sources, merged into one table: all NBN records plus the GBIF
records not already in NBN. For records in both, keep the NBN version. Further
filtering is done after merging.
**Records:** 243,105 NBN + 190,934 GBIF-only = 434,039. 1,727 GBIF records were
already in NBN and left out.
**Reason:** The sources overlap very little. Most GBIF records come from apps that
publish only to GBIF (eBird, Birda, iNaturalist), and most NBN records come from
"Birds (BTO+partners)", which is not in GBIF. Using only one source would lose a large
share of the records. NBN is kept for the overlap because it has grid references and
verification status.
**Note:** GBIF-only records use `gbifID` as record ID, because 36 of them have no
`occurrenceID`.

## 2026-11-11: Vitality filter
**Decision:** Remove records with vitality "dead". Keep "alive", "not recorded" and empty.
**Records:** 23 removed (all NBN).
**Reason:** Only "dead" is evidence against a live bird. "Not recorded" and empty carry
no information, the same as GBIF records, which have no vitality field. Filtering on
them would treat the two sources differently and drop whole NBN datasets that never
fill in vitality (e.g. Suffolk).

## 2026-11-11: Year filters
**Decision:** Remove records without a year, and keep only records from 1963 onwards.
**Records:** 18 removed without a year (all GBIF); 2 removed from 1900 (August and
December).
**Reason:** Records without a year can't be used in a yearly analysis. The two 1900
records look genuine but are isolated: the next record is from 1963. They tell us
nothing about the spread of the current population.

## 2026-11-11: Isle of Man
**Decision:** Remove records from the Isle of Man (`countryCode` = IM).
**Records:** 3 removed (all NBN).
**Reason:** The Isle of Man is not part of the UK, and the GBIF download (filtered on
United Kingdom) does not include it. Keeping it would make the two sources cover
different areas. With 3 records it has no effect on the analysis.

## 2026-11-11: GBIF data-quality flags
**Decision:** Keep all records with GBIF date or location flags. No records removed.
**Records checked (after the earlier filters):**
- `RECORDED_DATE_INVALID` (16) and `RECORDED_DATE_MISMATCH` (2): all have plausible
  years (1981–2025), mostly from one dataset (LERN Records). Likely a date-format issue
  at the provider. Only the year is needed for the analysis.
- `COUNTRY_INVALID` (6): all in central London, from the Estonian Ornithological
  Society dataset. Probably sightings by a visiting birder, with the dataset's default
  country (Estonia) clashing with the coordinates. Coordinates are plausible; only the
  country text is wrong.
- `CONTINENT_COORDINATE_MISMATCH`: 0 left (31 in the raw download, all removed by
  earlier steps).
**Reason:** None of the flags point to a wrong year or a wrong location.

## 2026-11-11: Spatial unit
**Decision:** Use 10 km squares (hectads, British National Grid) as the main spatial
unit. 2 km squares (tetrads) are used only as a comparison for the later period, when
10 km records are rare.
**Reason:**
- 10 km resolution records (2% of NBN) are concentrated in the early years, largely
  from the BTO atlases. Finer squares would drop much of the data for the start of
  the spread.
- GBIF records mostly have no coordinate uncertainty, and 54% come from locations used
  100+ times (birding hotspots). At 2 km, occupancy would largely reflect where birders
  go.
- All records fit inside a 10 km square, so none are lost.
**Consequence:** No coordinate uncertainty filter is needed for the main analysis.
**Note:** Northern Ireland records (~65) are placed on the British National Grid rather
than the Irish Grid, so that all records use the same squares.
**Reference:** Heald et al. (2019) used points, not grid squares, but their question
was the origin of the population, not the rate of spread. Skellam (1951) models the
spread through the occupied area, which grid squares give directly.

## Open decisions
- Origin of the spread
- Yearly range metric
- Correction for recording effort