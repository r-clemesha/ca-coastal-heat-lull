# Airport low-cloud and radiosonde inversion annual cycles

Supports Figure 3 and the cloud-base numbers in Section 3.3 of Clemesha et al., "Low Clouds and a Warm-Season
Lull in Extreme Daytime Heat Along Coastal California." The TX95 curves in Figure 3 (Miramar USW00093107, Oakland
USW00023230) are in `../stations/tx95_tx50_mean_curves_v6.csv`.

## Shared method
All curves use the same steps as TX95 (see `../stations/README.md`):
1. Calendar day 1–365 (29 Feb dropped).
2. Values from all years within ±5 days of each calendar day are pooled (11-day window) and averaged → `raw`.
3. 21-day running mean that wraps around the year → `smoothed`.
4. 95% confidence interval (`ci_lo`, `ci_hi`): 2.5th and 97.5th percentiles of the smoothed curve across 2000
   bootstrap replicates, each made by resampling whole years with replacement (seed 42).

## `airport_low_cloud_annual_cycles.csv`
Daytime low-cloud cover at San Diego (KSAN) and Monterey (KMRY), 1950–2024, from hourly airport observations in the
Integrated Surface Database (NOAA NCEI). Each day's value is the percentage of the 07, 10, 13 and 16 PST observations
that report cloud cover of at least 75% with cloud base below the threshold (following Schwartz et al., 2014).

| Column | Description | Units |
|---|---|---|
| `airport` | KSAN or KMRY | |
| `cloud_base_max_m` | cloud-base threshold: 400, 1000 or 2000 | m |
| `cdoy` | calendar day | |
| `raw`, `smoothed`, `ci_lo`, `ci_hi` | see Shared method | % |

Figure 3 uses the 2000-m threshold. The Section 3.3 cloud-base fractions are means of `smoothed` over the lull window
(minimum ±15 days): KSAN 15 May–14 Jun (`cdoy` 135–165), KMRY 15 Jul–14 Aug (`cdoy` 196–226).

## `inversion_annual_cycles.csv`
Marine-layer inversion at Miramar (San Diego) and Oakland from 12 UTC (04 PST) soundings, 1960–2026. The record
combines the legacy NOAA/ESRL Radiosonde Database (no longer online) with the Integrated Global Radiosonde Archive
v2.2 (IGRA; Durre et al., 2016), which fills gaps and extends it past the end of the legacy record (Miramar
2023, Oakland 2016).

| Column | Description | Units |
|---|---|---|
| `station` | MIRAMAR or OAKLAND | |
| `variable` | `ZBASE` = inversion base height; `DT_cond` = inversion strength (temperature increase across the inversion). Both are averaged over soundings that have an inversion | |
| `cdoy` | calendar day | |
| `raw`, `smoothed`, `ci_lo`, `ci_hi` | see Shared method | m above sea level (`ZBASE`); °C (`DT_cond`) |
