# Lull detection code

Detects extreme-heat lulls in station TX95 annual cycles and tests each one with a year-resampling bootstrap
(Section 2.2 and Text S2). Running it reproduces `../stations/all_stations_dip_results_v6.csv` exactly.

| File | Contents |
|---|---|
| `lull_detection.py` | The algorithm: TX95 and mean-Tmax annual cycles, smoothing, local minima and maxima, lull criteria. All settings are in `PARAMS` at the top. |
| `run_lull_detection.py` | Runs every station in the input file, bootstraps each candidate lull (2000 replicates, seed 42), and writes one row per station. |

## Run

```
cd code
python run_lull_detection.py
```

By default this reads `../stations/ghcnd_tmax_334stations_cleaned.csv.gz` and writes `all_stations_dip_results.csv`
in this folder; `--input` and `--output` override either. It takes about 45–60 minutes, almost all of it in the
bootstrap. Output columns are described in `../stations/README.md`.

## Requirements
Python 3 with numpy and pandas. Tested with Python 3.9.5, numpy 2.0.2 and pandas 2.3.3.

## License
MIT (see `LICENSE`).
