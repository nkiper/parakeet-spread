# Notes

Working notes: things to do, reminders for the write-up, and open questions.
Choices that have been made, and why, go in [`decisions.md`](decisions.md).

## Priorities for the remaining work

### Necessary

- [x] Spread rate: slope of √(area) against year, corrected and uncorrected, for
      1970–2025 and two phases (1970–2009, 2010–2025), atlas years left out (`04_effort-correction`)
- [x] Close the open decisions in `decisions.md`: yearly range metric, recording effort
      (with its limitations)
- [x] Check whether the acceleration after 2010 is real: NBN only (3.4 km/yr) and
      persistent squares (4.0 km/yr) both show it (`acceleration_checks.png`)
- [x] Choose the figures for the presentation: see "Presentation outline" below
- [x] Spread model: six centres from the 2025 map at one constant speed, speed and
      start years fitted to 1970–2025 (`05_spread-model`). Fits much better than London
      alone; new centres account for about 60 to 80% of the acceleration after 2010
- [x] Atlas check: BTO atlases as independent points (`04_effort-correction`, end)
- [x] Spread model and atlas check go in the presentation (see outline)
- [x] Skellam animation: three scenes, plus scene 3 without the walking-only line (`src/skellam_animation.py`)
- [ ] Limitations slide: coverage corrected but not intensity; atlas years; eBird
      growth; NBN download vs API versions; Great Britain only; observer effect in
      cities; stall after Bird Atlas 2007–11
- [ ] Presentation

### Nice to have (if there is time)

- [ ] Spread model: fit the start years to the maps (each centre's circle against the
      observed squares around it) instead of the total area. Would pin down the start
      years and size the circles correctly (`decisions.md`, "Open")
- [ ] Stricter "visited": a square counts as visited only if all four (or at least
      three) benchmarks were recorded that year. Addresses the intensity problem
      directly, using presence only (~1–2 hours)
- [ ] Range index per benchmark separately, plotted together (step 6)
- [ ] 5-year periods with binomial confidence intervals (step 8)
- [ ] Fixed set of regularly visited squares, to test the non-random-sample assumption

### Future work (outlook)

- Atlas check for 2007–11: the three older atlases are done as independent points
  (`04_effort-correction`, end). Bird Atlas 2007–11 is mixed with BirdTrack in the NBN
  data, so compare with the published atlas maps instead; also BBS trends (step 9)
- A real intensity correction: occupancy models (detection probability per visit) or
  methods such as Frescalo
- Origin of the spread, building on Heald et al. (2020), e.g. geographic profiling of
  the early records
- Duplicate sightings across systems (eBird and BirdTrack)
- Include Ireland (Irish Grid squares)
- Spread direction and speed per region, e.g. along urban areas

## Presentation outline

About 10 minutes. Files in `figures/`. First draft: `GHD_Presentation.pptx`; backup slides:
`GHD_Backup_Slides.pptx`. The outline below is the plan the draft started from.

**Title options:**

1. Faster, or from more places? The spread of ring-necked parakeets in Great Britain
2. Green invaders: 55 years of parakeet spread in Great Britain
3. From London parks to Glasgow: measuring how fast parakeets spread
4. Counting birds, correcting for birdwatchers: the spread of ring-necked parakeets
5. Spreading by leaps: ring-necked parakeets in Britain, 1970–2025

**Slides:**

1. Title
2. The question: an introduced species that now seems to be everywhere. How fast is it
   spreading, and is it speeding up?
3. Data: GBIF + NBN Atlas, ~434,000 records on 10 km squares. Records count sightings,
   not birds
4. What the data look like: `hectads_by_year.mp4`
5. How spread works (Skellam 1951), three slides; the videos have no text, so the
   explanation and formula go on the slides:
   - `skellam_1_one_bird.mp4`: one bird does a random walk
   - `skellam_2_walking.mp4`: many birds walking explore a circle, but the spread slows
     down (radius ∝ √time)
   - `skellam_3_breeding.mp4`: walking + breeding gives a constant speed, c = 2√(rD),
     so √(occupied area) rises in a straight line
6. The problem: more birdwatchers. `visited_squares_per_year.png`, atlas-year jumps
7. Effort correction: four common garden birds show which squares were visited.
   `range_corrected_vs_uncorrected.png`
8. Result: `spread_rate_by_period.png`, ~1.6 km/yr until 2009, ~4 km/yr from 2010
9. Is the speed-up real? `acceleration_checks.png`: holds with NBN only and with
   persistent squares
10. Independent check: `atlas_check.png`, breeding atlases lie on the trend line
11. Why the speed-up? Six centres from the 2025 map, one speed. `spread_model_curves.png`:
    RMSE 8.1 vs 15.2 km for London alone, 1.5 km/yr; new centres explain about 60 to
    80% of the speed-up, depending on the period
12. Where the model fits and where it doesn't: `spread_model_maps.png`. London fits;
    Cardiff has early records but stayed on the coast, so it's not a centre; about half
    of the 2025 squares lie outside the circles
13. Limitations: intensity not corrected, observer effect in cities, stall after Bird
    Atlas 2007–11, Great Britain only
14. Conclusions and outlook: ~1.5 km/yr per centre; the speed-up is mostly new centres,
    not faster spread. Next: fit the model to the maps, compare with Bird Atlas 2007–11

**Backup slides:** `spread_model_curves_persistent.png` (same model fitted to persistent
squares: same speed, 64–78% of the speed-up explained), `spread_model_speed_profile.png`, `sqrt_area_10km_vs_2km.png`, why
yearly rather than cumulative counts (one-off sightings stay forever, recording growth
builds up, errors carry forward).

## To do

- [x] Add the square assignment (`hectad`, `tetrad`) to `src/build_records.py`, so
      `records.parquet` includes the square IDs
- [x] Run the 2 km comparison for the period with few 10 km records (from the early 1990s)
- [ ] Check duplicate sightings entered in two systems (e.g. eBird and BirdTrack).
      For yearly occupancy of 10 km squares this hardly matters: duplicates fall in the
      same square in the same year, and a square counts once. It does matter if records
      per square are used, e.g. for recording effort.

- [x] Confirm the atlas explanation: check which datasets add the most 10 km squares in
      1981, 1988 and 2007–08 (confirmed for 1981 and 1988; 2008 consistent)

## For the write-up

### Credits

- GBIF.org (10 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.xnh55x
  (parakeet)
- GBIF.org (11 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.4yeq82
  (benchmark species)
- NBN Atlas API (https://records-ws.nbnatlas.org/), accessed 11 November 2026 (benchmark
  squares)
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
- Jumps in the yearly 10 km occupied area in 1981, 1988 and around 2008 (followed by a
  dip until about 2012) come from the BTO atlases, which survey every square
  systematically. They reflect recording effort, not spread: a direct example of why
  the range metric needs an effort correction.
  - 1981: Winter Atlas 1981/82–1983/84 covers 70 squares; the next source 6.
  - 1988: Breeding Atlas 1988–91 covers 63 squares; the next sources 12.
  - 2008: "Birds (BTO+partners)" covers 206 squares, against 132 in 2007 and 135 in
    2012. Consistent with Bird Atlas 2007–11, though the dataset name doesn't show it.
- 2 km vs 10 km (from 1992): the ratio of √(2 km area) to √(10 km area) rises from
  0.24 to 0.44 between 1992 and 2007, then stays at about 0.42–0.46. The rise is the
  same with NBN data only, so it is not caused by GBIF location accuracy. It fits more
  intensive recording (BirdTrack from 2004, then Bird Atlas 2007–11), possibly together
  with real filling in. From 2007 both square sizes grow at the same rate.
- Observer effect in the spread model (`05_spread-model`): cities have more birdwatchers
  and more escaped cage birds, so the urban "centres" may partly reflect where people look.
  The effort correction covers which squares were visited, not how intensively, so this is
  not corrected.
- Sparse 10 km squares (1–2 records in a year): NBN rises during the atlas years
  (37 in 2003 to 124 in 2008) and then stays at ~100–160; GBIF stays low until ~2015 and
  then rises steeply (to 169 in 2025). Recent growth at the edges of the range comes
  largely from eBird records with one or two records per square. These may be real
  spread, wandering birds, or eBird reaching new areas; the data can't tell them apart.

## Questions and ideas

- Origin of the spread: Heald et al. (2020) find no support for the popular origin
  stories and suggest repeated releases around southwest London. Use London as the core
  area rather than a single starting point?
- Yearly range metric: following Skellam (1951), plot √(occupied area) against year.
  Is it a straight line (constant spread rate)? Does it change around 1987–88, when
  records jump?
