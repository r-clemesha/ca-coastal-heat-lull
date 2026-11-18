# Data and code: Low Clouds and a Warm-Season Lull in Extreme Daytime Heat Along Coastal California

Clemesha, R. E. S., Weyant, A., Campbell, I., Guirguis, K., Iacobellis, S. F., Yao, P., Gershunov, A., Cayan, D. R.,
Merrifield, M. A., O'Brien, T. A., & Small, I. (2026). Data from: Low clouds and a warm-season lull in extreme
daytime heat along coastal California [Dataset]. UC San Diego Library Digital Collections.
https://doi.org/10.6075/J09C6ZMZ

Derived data and code supporting the manuscript submitted to *Geophysical Research Letters*. Primary datasets are
publicly available and are cited, not repeated, here.

## Contents

| Folder | Contents | Supports |
|---|---|---|
| `stations/` | Input station Tmax (334 stations), smoothed TX95 / median / mean Tmax annual cycles, lull detection and bootstrap results | Figures 1–2, S1–S3; station counts and lull statistics |
| `fig3_cloud_inversion/` | Airport daytime low-cloud annual cycles (San Diego, Monterey) and radiosonde inversion annual cycles (Miramar, Oakland) | Figure 3; Section 3.3 |
| `goes_low_cloud/` | GOES-West daytime low-cloud cover for pre-lull, lull and post-lull periods, 1996–2025 | Figures 4 and S4 |
| `code/` | Lull detection code; reproduces `stations/all_stations_dip_results_v6.csv` exactly | Section 2.2, Text S2 |

Each folder has its own README describing the files, columns, units and methods.

## Primary data sources
- Station Tmax: GHCN-Daily v3 (Menne et al., 2012), https://doi.org/10.7289/V5D21VHZ
- Gridded Tmax (Figure 4): nClimGrid-Daily v1 (Durre et al., 2022), https://doi.org/10.25921/c4gt-r169
- Airport cloud observations: Integrated Surface Database (NOAA NCEI)
- Radiosondes: IGRA v2.2 (Durre et al., 2016), https://doi.org/10.7289/V5X63K0Q, and the legacy NOAA/ESRL Radiosonde
  Database
- GOES-West low-cloud record (Clemesha et al., 2016); 1996–2020 archived at https://doi.org/10.6075/J0RN3825

## Conventions
- "Dip" in file and column names means the same as "lull" in the paper.
- `cdoy` is day of year on a 365-day calendar (1 Jan = 1, 1 Mar = 60, 31 Dec = 365; 29 Feb dropped).
- Temperatures are in °C.

## License
Data: CC BY 4.0. Code: MIT. See `LICENSE`.
