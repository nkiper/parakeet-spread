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
**Records:** 232,722
**Reason:** Same column standard as GBIF, which makes comparison and duplicate
detection easier. Includes grid reference and verification status.
**Licence note:** Records come from many data partners under CC-BY-NC licence. Credit the NBN Atlas and data partners in README and slides.
**Citation:** NBN Atlas occurrence download at NBN Atlas [https://nbnatlas.org/] accessed on 10 November 2026.

## 2026-11-10: Raw data storage
**Decision:** Store raw downloads in data/raw/, excluded from Git via .gitignore.
**Reason:** Files are large. The data can be re-downloaded using the GBIF DOI and the
NBN query documented above.

## Open decisions
- Main data source: GBIF, NBN Atlas, or merged (after comparing coverage, overlap and quality)
- Spatial unit (points or grid squares, and which size)
- Origin of the spread
- Yearly range metric
- Correction for recording effort