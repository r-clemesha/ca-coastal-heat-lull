# GOES-West daytime coastal low-cloud period climatologies, 1996–2025

Supports Figure 4 (cloud panels) and Figure S4 of Clemesha et al., "Low Clouds and a Warm-Season Lull in Extreme
Daytime Heat Along Coastal California."

## Source
Half-hourly, ~4-km GOES-West coastal low-cloud record (detection algorithm described and validated in Clemesha et al.,
2016, GRL, https://doi.org/10.1002/2015GL067081). The 1996–2020 portion of the record is archived in Clemesha et al.
(2023), UC San Diego Library Digital Collections, https://doi.org/10.6075/J0RN3825. Here the record is extended through
2025.

## Method
- Years: 1996–2025 (30 warm seasons).
- Daytime window: half-hourly retrievals starting 07:00–13:30 PST (14 slots per day; 8 AM–3 PM PDT).
- Low-cloud cover (%) = 100 × (retrievals with low cloud detected) / (valid retrievals), pooled over all days in the
  period and all years.
- Periods (same calendar dates every year):

| Region | P1 (pre-lull) | P2 (lull) | P3 (post-lull) |
|---|---|---|---|
| SoCal | 1–20 May | 21 May–9 Jun | 10–30 Jun |
| NorCalExt | 12 Jun–1 Jul | 20 Jul–8 Aug | 9–29 Aug |

- Grid: regular 0.04° lon/lat. SoCal 120.96–115.04°W, 32.52–35.44°N; NorCalExt 124.60–120.20°W, 35.32–39.00°N.
- Produced by `submonthly_climo_30yrs_8AM3PM_fixwin_v1.R` (7 Nov 2026).

## Files
One row per grid cell. `NA` = no valid retrievals at that cell.

| File | Columns | Units |
|---|---|---|
| `climo_P1P2P3_SoCal_8AM3PM_local_1996to2025.csv` | `lon`, `lat`, `P1_CLC_pct`, `P2_CLC_pct`, `P3_CLC_pct` | °E, °N, % |
| `climo_P1P2P3_NorCalExt_8AM3PM_local_1996to2025.csv` | same | same |

Period means are shown in Figure S4. Figure 4 shows the differences in percentage points:
lull − pre-lull = `P2_CLC_pct − P1_CLC_pct`; post-lull − lull = `P3_CLC_pct − P2_CLC_pct`.
