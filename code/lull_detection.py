"""
Extreme-heat lull detection (Clemesha et al., Section 2.2 and Text S2).

A lull is a robust warm-season local minimum in the smoothed calendar-day 95th percentile of daily maximum
temperature (TX95). This module holds the building blocks:

  1. calendar_day()          map dates to a 365-day calendar (29 Feb dropped)
  2. percentile_cycle()      TX95 (or any percentile) for each calendar day, pooling an 11-day window
  3. mean_cycle()            mean Tmax for each calendar day, same pooling (used to locate winter)
  4. smooth()                21-day running mean that wraps around the end of the year
  5. find_extrema()          local minima / maxima of a smoothed annual cycle
  6. detect_lull()           apply the lull criteria to the smoothed cycles

Days are numbered 1-365 in calendar_day() and in the output, and 0-364 (array positions) inside the functions.

Note: the output files call a lull a "dip"; the two words mean the same thing.
"""

import numpy as np
import pandas as pd


# All tunable settings in one place. Values are those used in the paper.
PARAMS = {
    # TX95 annual cycle
    "percentile":         95,    # percentile of Tmax (95 -> TX95)
    "half_window":        5,     # pool +/-5 days around each calendar day (11-day window)
    "min_values":         20,    # need at least this many Tmax values to compute a calendar day

    # Smoothing
    "smooth_window":      21,    # running-mean width, days

    # Local minima / maxima
    "extrema_half_win":   15,    # a point is an extremum if it is the lowest/highest within +/-15 days ...
    "extrema_tol":        0.1,   # ... allowing 0.1 degC of tolerance
    "cluster_radius":     10,    # extrema within 10 days of each other are merged; the most extreme is kept

    # Exclude the winter trough (a winter minimum is not a lull)
    "trough_dist":        70,    # a minimum within 70 days of the coldest day of the mean cycle ...
    "trough_ceiling_pct": 0.15,  # ... AND where mean Tmax is in the lowest 15% of its annual range is excluded

    # Shoulder = TX95 peak before the lull; recovery = TX95 peak after it
    "min_shoulder_dist":  10,    # shoulder must lie 10-90 days before the minimum
    "max_shoulder_dist":  90,
    "min_recovery_dist":  10,    # recovery peak must lie 10-90 days after the minimum
    "max_recovery_dist":  90,

    # Size threshold, applied to both the drop and the recovery:
    # at least max(1.0 degC, 5% of the station's TX95 annual range)
    "min_mag_abs":        1.0,   # degC
    "min_mag_pct":        0.05,  # fraction of TX95 annual range

    # Skip stations whose TX95 barely varies through the year
    "min_annual_range":   1.0,   # degC
}


def calendar_day(dates):
    """Day of year on a 365-day calendar: 1 Jan = 1, 28 Feb = 59, 1 Mar = 60, 31 Dec = 365.

    29 Feb gets 0 so the caller can drop it. Later days in leap years shift back by one so that
    every year uses the same numbering.
    """
    dates = pd.DatetimeIndex(dates)
    day_of_year = np.asarray(dates.dayofyear, dtype=np.int32)
    is_leap = np.asarray(dates.is_leap_year)
    is_feb29 = is_leap & (np.asarray(dates.month) == 2) & (np.asarray(dates.day) == 29)

    result = day_of_year.copy()
    result[is_feb29] = 0
    result[is_leap & ~is_feb29 & (day_of_year > 60)] -= 1
    return result


def _window_mask(day_numbers, day):
    """True for every value whose calendar day is within +/-half_window of `day` (wrapping at year end)."""
    hw = PARAMS["half_window"]
    mask = np.zeros(len(day_numbers), dtype=bool)
    for offset in range(-hw, hw + 1):
        mask |= (day_numbers == ((day - 1 + offset) % 365) + 1)
    return mask


def percentile_cycle(tmax, day_numbers):
    """Percentile of Tmax (default 95th = TX95) for each calendar day.

    For each day, Tmax from all years within +/-5 days are pooled (an 11-day window) and the
    95th percentile is taken. Days with fewer than 20 values are left as NaN.
    """
    cycle = np.full(365, np.nan)
    for day in range(1, 366):
        values = tmax[_window_mask(day_numbers, day)]
        if len(values) >= PARAMS["min_values"]:
            cycle[day - 1] = np.percentile(values, PARAMS["percentile"])
    return cycle


def mean_cycle(tmax, day_numbers):
    """Mean Tmax for each calendar day, pooled the same way as percentile_cycle().

    Used only to locate the winter trough, so that winter minima are not counted as lulls.
    """
    cycle = np.full(365, np.nan)
    for day in range(1, 366):
        values = tmax[_window_mask(day_numbers, day)]
        if len(values) >= PARAMS["min_values"]:
            cycle[day - 1] = np.nanmean(values)
    return cycle


def smooth(values):
    """21-day running mean that wraps around the year (late December is averaged with early January)."""
    w = PARAMS["smooth_window"]
    hw = w // 2
    padded = np.concatenate([values[-hw:], values, values[:hw]])
    smoothed = np.convolve(padded, np.ones(w) / w, mode="same")
    return smoothed[hw: hw + len(values)]


def find_extrema(curve, mode):
    """Local minima (mode="min") or maxima (mode="max") of a smoothed 365-day cycle.

    A day qualifies if it is within 0.1 degC of the lowest (highest) value in the surrounding +/-15 days.
    Qualifying days within 10 days of each other form one group (wrapping at year end), and the most
    extreme day of each group is returned. Returns array positions 0-364.
    """
    hw, tol, radius = PARAMS["extrema_half_win"], PARAMS["extrema_tol"], PARAMS["cluster_radius"]
    n = len(curve)

    candidates = []
    for i in range(n):
        neighbours = [curve[(i + j) % n] for j in range(-hw, hw + 1)]
        if mode == "min" and curve[i] <= min(neighbours) + tol:
            candidates.append(i)
        elif mode == "max" and curve[i] >= max(neighbours) - tol:
            candidates.append(i)
    if not candidates:
        return []

    # Group neighbouring candidates
    groups = [[candidates[0]]]
    for c in candidates[1:]:
        if c - groups[-1][-1] <= radius:
            groups[-1].append(c)
        else:
            groups.append([c])
    # A group that spans 31 Dec / 1 Jan is joined into one
    if len(groups) > 1 and (n - groups[-1][-1] + groups[0][0]) <= radius:
        groups[0] = groups[-1] + groups[0]
        groups = groups[:-1]

    pick = np.argmin if mode == "min" else np.argmax
    return [g[pick([curve[c] for c in g])] for g in groups]


def nearest_peak(peaks, day, direction):
    """Nearest TX95 peak 10-90 days before (direction="before") or after ("after") array position `day`.

    Returns None if there is no peak in that range.
    """
    if direction == "before":
        lo, hi = PARAMS["min_shoulder_dist"], PARAMS["max_shoulder_dist"]
    else:
        lo, hi = PARAMS["min_recovery_dist"], PARAMS["max_recovery_dist"]
    best, best_dist = None, 999
    for peak in peaks:
        dist = (day - peak) % 365 if direction == "before" else (peak - day) % 365
        if lo <= dist <= hi and dist < best_dist:
            best, best_dist = peak, dist
    return best


def detect_lull(tx95_smooth, mean_smooth):
    """Find lulls in a station's smoothed TX95 cycle.

    Steps:
      1. Skip the station if its TX95 annual range is under 1 degC.
      2. Find local minima and maxima of TX95.
      3. Drop minima in the winter trough: within 70 days of the coldest day of the mean-Tmax cycle
         and where mean Tmax is in the lowest 15% of its annual range.
      4. For each remaining minimum, take the nearest TX95 peak 10-90 days earlier (the shoulder).
         Keep the minimum only if the drop (shoulder - minimum) is at least max(1 degC, 5% of the
         TX95 annual range).
      5. Take the nearest TX95 peak 10-90 days later. If there is none (TX95 rises steadily),
         use TX95 90 days after the minimum. The recovery (that value - minimum) must pass the same
         threshold.

    Returns a list of lulls, largest drop first. Each is a dict with bottom_doy and shoulder_doy
    (calendar days 1-365), drop and recovery (degC), and recovery_type.
    """
    # Step 1
    tx95_range = np.nanmax(tx95_smooth) - np.nanmin(tx95_smooth)
    if tx95_range < PARAMS["min_annual_range"]:
        return []
    threshold = max(PARAMS["min_mag_abs"], PARAMS["min_mag_pct"] * tx95_range)

    # Step 2
    minima = find_extrema(tx95_smooth, mode="min")
    peaks = find_extrema(tx95_smooth, mode="max")

    # Step 3
    coldest_day = int(np.argmin(mean_smooth))
    mean_range = np.nanmax(mean_smooth) - np.nanmin(mean_smooth)
    trough_ceiling = np.nanmin(mean_smooth) + PARAMS["trough_ceiling_pct"] * mean_range
    candidates = []
    for m in minima:
        days_from_coldest = min(abs(m - coldest_day), 365 - abs(m - coldest_day))
        in_winter_trough = days_from_coldest <= PARAMS["trough_dist"] and mean_smooth[m] < trough_ceiling
        if not in_winter_trough:
            candidates.append(m)

    lulls = []
    for bottom in candidates:
        # Step 4
        shoulder = nearest_peak(peaks, bottom, "before")
        if shoulder is None:
            continue
        drop = tx95_smooth[shoulder] - tx95_smooth[bottom]
        if drop < threshold:
            continue

        # Step 5
        recovery_peak = nearest_peak(peaks, bottom, "after")
        if recovery_peak is not None:
            recovery = tx95_smooth[recovery_peak] - tx95_smooth[bottom]
            recovery_type = "local_max"
        else:
            recovery = tx95_smooth[(bottom + PARAMS["max_recovery_dist"]) % 365] - tx95_smooth[bottom]
            recovery_type = "monotonic_fallback"
        if recovery < threshold:
            continue

        lulls.append({
            "bottom_doy": bottom + 1,
            "shoulder_doy": shoulder + 1,
            "drop": round(drop, 4),
            "recovery": round(recovery, 4),
            "recovery_type": recovery_type,
        })

    lulls.sort(key=lambda x: x["drop"], reverse=True)
    return lulls
