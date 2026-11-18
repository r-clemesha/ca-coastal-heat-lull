#!/usr/bin/env python3
"""
Run lull detection on all stations and test each lull with a year-resampling bootstrap
(Clemesha et al., Section 2.2 and Text S2).

Usage:
    python run_lull_detection.py [--input INPUT] [--output OUTPUT]

Defaults:
    input:  ../stations/ghcnd_tmax_334stations_cleaned.csv.gz   (station, name, latitude, longitude, elevation, date, tmax)
    output: all_stations_dip_results.csv

Output columns are described in ../stations/README.md. Runtime is about 45-60 minutes, almost all of it in
the bootstrap (2000 replicates for each station with a candidate lull). The random seed is fixed, so repeated
runs give identical results.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from lull_detection import (PARAMS, calendar_day, percentile_cycle, mean_cycle, smooth,
                            find_extrema, detect_lull)

N_BOOTSTRAP = 2000
RANDOM_SEED = 42
MIN_DAYS = 365 * 5   # stations need at least 5 years of valid Tmax

HERE = Path(__file__).parent
DEFAULT_INPUT = HERE.parent / "stations" / "ghcnd_tmax_334stations_cleaned.csv.gz"
DEFAULT_OUTPUT = HERE / "all_stations_dip_results.csv"


def bootstrap_drop(tmax, day_numbers, years, lull):
    """Bootstrap distribution of the lull drop (shoulder TX95 - minimum TX95).

    Whole calendar years are resampled with replacement, so days within a year stay together and
    are not treated as independent. In each replicate the minimum stays on the observed day; TX95 is
    recomputed and the nearest peak 10-90 days earlier is found again. A replicate with no such peak,
    or with TX95 higher at the minimum than at the peak, counts as a drop of 0.
    """
    bottom = lull["bottom_doy"] - 1
    unique_years = np.unique(years)

    drops = []
    for _ in range(N_BOOTSTRAP):
        sampled_years = np.random.choice(unique_years, size=len(unique_years), replace=True)
        idx = np.concatenate([np.where(years == y)[0] for y in sampled_years])

        tx95 = percentile_cycle(tmax[idx], day_numbers[idx])
        if np.any(np.isnan(tx95)):
            drops.append(0.0)
            continue
        tx95 = smooth(tx95)

        # Nearest peak 10-90 days before the fixed minimum
        shoulder, shoulder_dist = None, 999
        for peak in find_extrema(tx95, mode="max"):
            dist = (bottom - peak) % 365
            if PARAMS["min_shoulder_dist"] <= dist <= PARAMS["max_shoulder_dist"] and dist < shoulder_dist:
                shoulder, shoulder_dist = peak, dist

        drops.append(max(tx95[shoulder] - tx95[bottom], 0.0) if shoulder is not None else 0.0)

    return np.array(drops)


def no_lull_row(info, verdict):
    """Output row for a station without a lull."""
    return {**info, "has_dip": False, "bottom_doy": "", "drop": "", "recovery": "", "shoulder_doy": "",
            "boot_drop_med": "", "boot_drop_ci_lo": "", "boot_drop_ci_hi": "", "boot_drop_pgt0": "",
            "verdict": verdict}


def process_station(stn):
    """Detect and bootstrap-test the lull at one station. Returns one output row."""
    tmax = stn["tmax"].values.astype(np.float64)
    dates = pd.DatetimeIndex(stn["date"])

    # Drop 29 Feb and missing values
    day_numbers = calendar_day(dates)
    keep = (day_numbers > 0) & ~np.isnan(tmax)
    tmax, day_numbers, years = tmax[keep], day_numbers[keep], dates[keep].year.values

    info = {"station": stn["station"].iloc[0], "name": stn["name"].iloc[0],
            "lat": stn["latitude"].iloc[0], "lon": stn["longitude"].iloc[0],
            "n_years": len(np.unique(years))}

    if len(tmax) < MIN_DAYS:
        return no_lull_row(info, "INSUFFICIENT DATA")

    tx95 = percentile_cycle(tmax, day_numbers)
    tmean = mean_cycle(tmax, day_numbers)
    if np.any(np.isnan(tx95)) or np.any(np.isnan(tmean)):
        return no_lull_row(info, "INCOMPLETE CYCLE")

    lulls = detect_lull(smooth(tx95), smooth(tmean))
    if not lulls:
        return no_lull_row(info, "NO DIP")

    # Test the largest lull. It is counted (RESOLVED) only if the lower end of the bootstrap
    # 95% confidence interval of the drop is above zero.
    lull = lulls[0]
    drops = bootstrap_drop(tmax, day_numbers, years, lull)
    ci_lo, ci_hi = np.percentile(drops, 2.5), np.percentile(drops, 97.5)

    return {**info, "has_dip": True,
            "bottom_doy": lull["bottom_doy"], "drop": round(lull["drop"], 4),
            "recovery": round(lull["recovery"], 4), "shoulder_doy": lull["shoulder_doy"],
            "boot_drop_med": round(np.median(drops), 4),
            "boot_drop_ci_lo": round(ci_lo, 4), "boot_drop_ci_hi": round(ci_hi, 4),
            "boot_drop_pgt0": round(np.mean(drops > 0), 4),
            "verdict": "RESOLVED" if ci_lo > 0 else "NO DIP"}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    df = pd.read_csv(args.input, parse_dates=["date"], dtype={"station": str, "name": str})
    stations = df["station"].unique()
    print(f"{len(df):,} rows, {len(stations)} stations")

    # Stations are processed in file order with one random sequence, so the seed fixes every result.
    np.random.seed(RANDOM_SEED)
    rows = []
    for i, station in enumerate(stations, 1):
        row = process_station(df[df["station"] == station].sort_values("date"))
        rows.append(row)
        if row["has_dip"]:
            print(f"[{i}/{len(stations)}] {station} {row['name'][:30]}: minimum day {row['bottom_doy']}, "
                  f"drop {row['drop']:.2f} degC, {row['verdict']}", flush=True)

    results = pd.DataFrame(rows)
    results.to_csv(args.output, index=False)
    print(f"\n{len(results)} stations; candidate lulls: {int(results['has_dip'].sum())}; "
          f"RESOLVED: {int((results['verdict'] == 'RESOLVED').sum())}\nSaved {args.output}")


if __name__ == "__main__":
    main()
