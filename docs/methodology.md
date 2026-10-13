# Methods and interpretation

Inputs are the official public annual ridership archives, filtered by `Start_Time` month. `Start_Station_Id` and `End_Station_Id` are normalised to remove CSV-derived `.0` suffixes. No trips are silently removed from the prepared monthly Parquet. Individual notebook analyses explicitly specify their own subset.

`Bike_Model` is mapped provisionally: labels starting with `EFIT` → Electric; `ICONIC` → Conventional; all other or missing values → Unknown. Check unique model labels on other years.

A bike-share trip begins when a bike is unlocked and ends when it is docked. Observed duration may include stationary time and detours. Station-to-station records cannot establish a route travelled. Route visualisations require an additional open routing graph and time-appropriate station locations, planned for a separate release.

Data attribution: Contains information licensed under the Open Government Licence – Toronto. https://open.toronto.ca/open-data-licence/
