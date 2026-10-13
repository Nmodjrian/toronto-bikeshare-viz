# Toronto Bike Share Viz Lab 🚲

Open-source, reproducible notebooks for exploring **Bike Share Toronto** trip records. Start with official City of Toronto data; no proprietary account and no CSC setup required.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/download_data.py --year 2024
python scripts/prepare_data.py --year 2024 --month 6
jupyter lab
```

Open notebooks in numerical order. The first three notebooks work **without** GraphHopper or a route database.

## Notebooks

- `01_explore_ridership.ipynb` — daily trips, user types, trip-duration distribution
- `02_daily_cycling_patterns.ipynb` — day × hour heatmap and weekday/weekend comparisons
- `03_ebike_vs_regular.ipynb` — e-bike/conventional daily trends and e-bike share

A later release will include portable GraphHopper reconstruction, route-glow maps and animations. We deliberately do **not** ship CSC-only paths, previously generated route files, or unverified June 2024 station locations.

## Data source and attribution

Contains information licensed under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-licence/).

Dataset: [Bike Share Toronto Ridership Data](https://open.toronto.ca/dataset/bike-share-toronto-ridership-data/). The download script discovers the official annual resource through the City of Toronto Open Data CKAN API. No ridership records are committed to this repository.

Inspirational reference: [Jeff Allen, Mapping Bike Share Trips in Toronto](https://schoolofcities.github.io/bike-share-toronto/trips-062024). This is an independent teaching and visualisation project, not an exact historical replication and not endorsed by the City or the School of Cities.

## Interpretation and limitations

Trip counts reflect recorded Bike Share Toronto rentals, not every bicycle trip in Toronto. Station OD pairs are **not** GPS tracks. Observed trip duration includes stops and is not automatically riding time. E-bike availability and membership patterns can confound direct comparisons. Bike model labels may change across annual datasets; unknown labels are retained as `Unknown`.

## Contributing

Issues and pull requests are welcome. Please provide data-year information when reporting problems. Do not upload raw ridership data, SQLite databases, generated route geometry or secrets in pull requests.

## Licensing

Source code: MIT (see `LICENSE`). City of Toronto data remain under the City's Open Government Licence and are not relicensed by this repository.

## Version 0.2 — modelled cycling route maps and animations

After the basic quick start, follow **[Route reconstruction instructions](docs/routing.md)**. New notebooks:

- `04_glowing_cycling_maps.ipynb` — monthly two-colour overlay (cyan electric, magenta conventional)
- `05_daily_animations.ipynb` — 30 daily two-colour PNGs, animated GIF, and bike-type activity chart

These notebooks need the optional local GraphHopper routing workflow and a contemporary GBFS station snapshot; they **do not** work from ridership CSV data alone. For June 2024, the station and OSM inputs must be checked against historical versions before scientific inference. All mapped routes are hypothetical modelled OD paths, not GPS observations.
