# Data retrieval script for forecast and historical weather data
This script automatically retrieves forecast and historical weather data from
different OpenMeteo Weather APIs (Weather Forecast APi, Historical Forecast
API and Historical Weather API) and saves the results in CSV format.

The following queries are carried out in the main.py module (for Vienna, Austria):
- historical weather data from 2022 to the current year (included)
- weather forecast for the 7 days (up to 16 days, depending on the used model)
- historical weather forecast from the past day

The results are exported as csv and tm2 files.