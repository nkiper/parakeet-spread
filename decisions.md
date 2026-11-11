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
**The 2010–2025 rate depends on the stall after the Bird Atlas:** the corrected range peaks in 2008 (√area 152 km), stalls until 2013 (136 km), and then rises steeply (4.4 km/yr for 2014–2025). The stall lowers the 2010–2025 slope rather than inflating it, but the recent rate depends on where the period starts: windows that span the stall give 3.1 km/yr (2005–2025) and 3.3 km/yr (2007–2025). If the 2008 peak and the stall are recording artefacts (more recording during the atlas, less after it), part of the steep rise from 2014 is catch-up, and the underlying recent rate is closer to 3 km/yr. The data can't tell; "about 4 km/yr" describes the rise after the stall.
**Note:** `spread_rates.csv` in Git still had the earlier sub-periods (1970–89, 1990–2009); the cell had been changed to 1970–2009 and 2010–2025 but not re-run. Re-run on 11 Nov 2026; the values above are from the corrected file.

### 2026-11-11: BTO atlases as an independent check
**Decision:** Compare the parakeet squares of three BTO atlases with the 1970–2009 trend line (`04_effort-correction`, end): First Breeding Atlas 1968–72, Winter Atlas 1981/82–1983/84, Second Breeding Atlas 1988–91. Bird Atlas 2007–11 is not used.
**Reason:** The atlases surveyed every square, so they need no effort correction, and their start years are left out of the fits, so they are independent of the trend line.
**How:** An atlas range is cumulative over its years and the trend line is yearly, so the atlas is compared with the line between the middle and the end of the atlas period. A second comparison: the non-atlas data from the same years, pooled the same way (atlas start year left out).
**Result:**

| Atlas | Squares | √area atlas | Trend line | Non-atlas, pooled |
|---|---|---|---|---|
| First Breeding 1968–72 | 4 | 20 km | 18–24 km | 33 km |
| Winter 1981–84 | 70 | 84 km | 55–59 km | 89 km |
| Second Breeding 1988–91 | 63 | 79 km | 76–80 km | 102 km |

The breeding atlases confirm the trend line. The Winter Atlas lies above it, but agrees with the other data from those winters: wandering in winter and three pooled winters, or a real high in the early 1980s.
**Bird Atlas 2007–11:** in the NBN Atlas it is part of "Birds (BTO+partners)" together with BirdTrack, and no field (dates, sampling protocol) separates them. Comparison with the published maps is future work.

## Spread model

### 2026-11-11: Constant-speed circles from five urban centres
**Decision:** Model the spread as circles growing at one constant speed from five centres: London, Birmingham, Manchester, Glasgow, Cardiff (`05_spread-model`). Only spread is modelled, not population size.
- **Occupied:** a 10 km land square in Great Britain whose centre lies within c × (years since start) of a centre, plus the centre's own square.
- **Parameters:** one speed c for all centres, and one start year per centre, all fitted.
- **Fit:** least squares on √(area) against the effort-corrected range, 1970–2025, atlas start years left out. Start years are whole years, from 5 years before the first parakeet record within 25 km of the city (birds may have been there before they were first recorded) to 2025.
- **Search:** London only (2 parameters) exhaustively; five centres (6 parameters) by coordinate descent from 40 random starting points (seeded), keeping the best.
- **Two models:** London only, and five centres.

**Reason:**
- Skellam (1951): random dispersal plus growth gives a front moving at constant speed, so the long-run result (a circle growing at constant speed) is enough when only the spread is of interest. A full reaction-diffusion simulation would need a growth rate and a dispersal rate separately, which occupancy data can't determine.
- One shared speed: the question is whether one speed with several centres explains the curve, rather than faster spread.
- The centres are the largest cities, where escaped or released pet birds are most likely, and they are visible as centres in the animation. The goal is to explain the current spread, not to predict it, so choosing the centres and fitting the whole period with hindsight is fine.
- Start years bounded by the first records, so the fit can't place a centre long before any bird was seen there.

**Result:**

| | London only | Five centres |
|---|---|---|
| Speed | 2.1 km/yr | 1.5 km/yr (within 10% of best RMSE: 1.5–1.9) |
| Start years | London 1970 | London 1963, Manchester 1988, Cardiff 1995, Glasgow 2002, Birmingham 2005 |
| RMSE 1970–2025 | 15.1 km | 8.8 km |
| Model spread rate 1970–2009 → 2010–2025 | 2.0 → 1.6 km/yr | 1.7 → 2.8 km/yr (observed 1.7 → 4.0) |

- Five centres fit much better, before and after 2010; the speed matches the pre-2010 rate from `04`. At one constant speed, the new centres account for about half of the acceleration measured over 2010–2025.
- That share depends on the window, because of the stall after the Bird Atlas (see "Results and limitations" above). Model against observed: 2010–2025 2.8 vs 4.0 km/yr (about half); 2007–2025 2.8 vs 3.3 (about 70%); 2005–2025 2.8 vs 3.1 (about 75%), each relative to London alone (1.6–1.7 km/yr). A smooth constant-speed model can't follow a stall followed by a steep rise.
- An earlier version fitted the speed to 1970–2009 only and projected it (start years from a rule, not fitted). Its post-2010 slope was steeper (3.3 km/yr, "two-thirds"), but only because its curve ran far above the data in 2010–2019 (RMSE 26.9 km after 2010, against 11.8 km for the full fit).
- London starts at its lower bound, so the fit would place it earlier still.
- The other start years are poorly determined: near-best fits (within 5% of the best RMSE) put Manchester at 1988–2005, Glasgow 1991–2007, Birmingham 1998–2008, Cardiff 1983–2007. Consistent is the order: London first, the others from the late 1980s to the 2000s.

**Limitations:**
- Observer effect: cities have more birdwatchers and more escapes; the effort correction doesn't cover intensity.
- Start years are fitted to the total area only, which doesn't say which city added which squares; fitting to the maps would determine them better.
- Cardiff doesn't fit: records from 1972, but it stayed in the coastal urban belt and hardly spread inland. Swansea was occupied by 1983, too early for spread from Cardiff at this speed. Coast, towns and recording effort coincide there and can't be separated.
- About half of the squares occupied in 2025 (262 of 543) lie outside all five circles (clusters near Nottingham, Southampton, Newcastle, East Kent, and many scattered squares).
- Circles ignore the sea and habitat.
- The model falls behind the observed range after 2020.

## Open

- Origin of the spread: future work, building on Heald et al. (2019).
