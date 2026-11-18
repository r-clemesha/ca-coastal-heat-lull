# Station TX95 annual cycles and extreme-heat lull detection results (334 stations)

Supports Figures 1–2 and S1–S3, and the station counts and lull statistics in the text, of Clemesha et al., "Low
Clouds and a Warm-Season Lull in Extreme Daytime Heat Along Coastal California."

Input data: daily maximum temperature (Tmax) from GHCN-Daily v3 (Menne et al., 2012,
https://doi.org/10.7289/V5D21VHZ). Station selection is described in Text S1 and detection in Section 2.2 and Text S2.
"Dip" in file and column names is the same thing as the "lull" in the paper.

## Calendar day (`cdoy`, `*_doy`)
Day of year on a 365-day calendar: 1 Jan = 1, 28 Feb = 59, 1 Mar = 60, 31 Dec = 365. 29 Feb is dropped.

## `tx95_tx50_mean_curves_v6.csv` (334 stations × 365 days)
| Column | Description | Units |
|---|---|---|
| `station` | GHCN-Daily station ID | |
| `cdoy` | calendar day (see above) | |
| `tx95` | smoothed 95th percentile of Tmax (TX95) | °C |
| `tx50` | smoothed median Tmax | °C |
| `mean` | smoothed mean Tmax | °C |

Each curve pools Tmax from all years within ±5 days of each calendar day (11-day window), then smooths with a
21-day circular running mean. These are the curves the lull detection uses.

## `all_stations_dip_results_v6.csv` (one row per station)
| Column | Description | Units |
|---|---|---|
| `station`, `name`, `lat`, `lon` | GHCN-Daily ID, name, latitude, longitude | °N, °E |
| `n_years` | number of years with valid data | |
| `has_dip` | a candidate lull passed all detection criteria on the full record | True/False |
| `bottom_doy` | calendar day of the TX95 lull minimum | |
| `shoulder_doy` | calendar day of the pre-lull TX95 maximum (shoulder) | |
| `drop` | TX95 at shoulder − TX95 at minimum | °C |
| `recovery` | rise in TX95 after the minimum | °C |
| `boot_drop_med`, `boot_drop_ci_lo`, `boot_drop_ci_hi` | median and 2.5th–97.5th percentiles of `drop` across 2000 year-resampling bootstrap replicates. In each replicate the minimum stays on the observed `bottom_doy` and the shoulder is searched for again; a replicate with no shoulder or a negative drop counts as 0 | °C |
| `boot_drop_pgt0` | fraction of replicates with `drop` > 0 | |
| `verdict` | `RESOLVED` = lull detected and `boot_drop_ci_lo` > 0 (the 37 lull stations in the paper); otherwise `NO DIP` | |

Four stations have `has_dip = True` but `verdict = NO DIP` because their bootstrap confidence interval reaches zero:
Monterey, San Luis Obispo Poly, El Toro MCAS, and Santo Tomás (MX).
