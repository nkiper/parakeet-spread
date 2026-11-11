# Notes

Working notes: things to do, reminders for the write-up, and open questions.
Choices that have been made, and why, go in [`decisions.md`](decisions.md).

## To do

- [x] Add the square assignment (`hectad`, `tetrad`) to `src/build_records.py`, so
      `records.parquet` includes the square IDs
- [ ] Run the 2 km comparison for the period with few 10 km records (from the early 1990s)
- [ ] Check duplicate sightings entered in two systems (e.g. eBird and BirdTrack).
      For yearly occupancy of 10 km squares this hardly matters: duplicates fall in the
      same square in the same year, and a square counts once. It does matter if records
      per square are used, e.g. for recording effort.

## For the write-up

### Credits

- GBIF.org (10 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.xnh55x
- NBN Atlas and its data partners (records under CC-BY-NC); thank all recorders
- Land outlines: Natural Earth (public domain)

### Caveats to mention

- Record counts are not bird counts. Recording effort grew strongly over time (e.g.
  eBird, BirdTrack), which inflates both record numbers and occupied area.
- 2026 is incomplete (data downloaded on 10 November 2026).
- Before about 1990, many NBN records have only 10 km resolution (largely BTO atlases).
- 54% of GBIF records come from locations used 100+ times (birding hotspots), and most
  GBIF records have no coordinate uncertainty.
- Northern Ireland records (~65) are placed on the British National Grid, not the
  Irish Grid.

## Questions and ideas

- Origin of the spread: Heald et al. (2019) find no support for the popular origin
  stories and suggest repeated releases around southwest London. Use London as the core
  area rather than a single starting point?
- Yearly range metric: following Skellam (1951), plot √(occupied area) against year.
  Is it a straight line (constant spread rate)? Does it change around 1987–88, when
  records jump?
