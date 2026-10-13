# Reconstructing routes (v0.2)

1. `python scripts/download_data.py --year 2024`
2. `python scripts/prepare_data.py --year 2024 --month 6`
3. `python scripts/download_stations.py` (live GBFS station snapshot, **not historic June 2024**)
4. Obtain a Toronto-area `.osm.pbf` extract legally from an OSM provider, save as `data/osm/toronto.osm.pbf` (not included). Record URL/date/license. Ensure it covers all selected stations.
5. Install Java 25+ and download GraphHopper **11.1** web JAR from Maven Central into a local location (e.g. `tools/graphhopper-web-11.1.jar`): `https://repo1.maven.org/maven2/com/graphhopper/graphhopper-web/11.1/graphhopper-web-11.1.jar`.
6. From the repository root start: `java -Xmx8g -jar tools/graphhopper-web-11.1.jar server config/graphhopper-bike.yml`
7. In another terminal, test `http://127.0.0.1:8989/health`, then run `python scripts/reconstruct_routes.py --year 2024 --month 6 --max-pairs 2000`.
8. Run notebook `04_glowing_cycling_maps.ipynb` and `05_daily_animations.ipynb`.

### Scaling and validity

The routing command caches each unique **directed** station pair in SQLite; reruns skip existing pairs. `--max-pairs 0` evaluates all coordinate-matched pairs but may take hours. It is normal to have unmapped trips due to missing historic station IDs, changed stations, invalid durations, missing bike models, or unavailable routes. Inspect error rows before comparing coverage. Both bike models share one ordinary-bike routing profile; there is no observed e-bike-specific path inference. **A 2026 snapshot of stations and OSM is not a historical reconstruction of June 2024**. Trip records do not provide observed GPS paths. Results are exploratory; document station matching, dates, and versioned source data before using for research conclusions.

This repository is independent of research-specific CSC working folders. No database, OSM extract, JAR or raw trip data is distributed.
