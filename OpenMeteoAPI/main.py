from ConvertToTM2.convert import TMY2
from openmeteo_api import setup_client, get_hourly_values, request_historical_data, request_forecast_data
from OpenMeteoAPI.utils import *

import pandas as pd

client = setup_client()

# interface between OpenMeteo and tmy2 format (corresponding variable names as 1 value pair per tuple)
INTERFACE = [
    ("temperature_2m", 'dry_bulb_temp'),
    ("relative_humidity_2m", 'rel_hum'),
    ("dew_point_2m", 'dew_point_temp'),
    ("rain", 'precipitable_water'),
    ("cloud_cover", 'total_sky_cover'),
    ("surface_pressure", 'atmos_pressure'),
    ("wind_speed_10m", 'wind_speed'),
    ("wind_direction_10m", 'wind_dir'),
    ("diffuse_radiation", 'diff_hor_rad'),
    ("direct_radiation", 'dir_norm_rad'),
]

# list of variables packed in OpenMeteo request
openmeteo_variables = [varnames[0] for varnames in INTERFACE]

latitude = 48.2085
longitude = 16.3721
year = 2023  # year of historical dataset

params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": openmeteo_variables,
    "timezone": "auto"
}

# send API requests
historical_response = request_historical_data(client, params, year)
forecast_response = request_forecast_data(client, params)

# convert response into dictionary
historical_dict = get_hourly_values(historical_response, openmeteo_variables)
forecast_dict = get_hourly_values(forecast_response, openmeteo_variables)

# todo: Datum wird in time zone +0 angegeben, also ist die Stundenspalte (wenn man eine andere Zeitzone hat) um
#  eine/mehrere Stunden verschoben. Deshalb ist eine entsprechende Korrektur an dieser Stelle nötig.

# convert response into pandas DataFrame
historical_df = pd.DataFrame(historical_dict)
forecast_df = pd.DataFrame(forecast_dict)

# remove leap day during leap years
if is_leap_year(year):
    historical_df = historical_df[~((historical_df.date.dt.month == 2) & (historical_df.date.dt.day == 29))]
if is_leap_year(forecast_df.date.dt.year[0]):
    forecast_df = forecast_df[~((forecast_df.date.dt.month == 2) & (forecast_df.date.dt.day == 29))]

# region FORECAST

# initialize tmy2 conversion
forecast_tm2 = TMY2(
    lat=forecast_response.Latitude(),
    long=forecast_response.Longitude(),
    time_zone=int(forecast_response.UtcOffsetSeconds() / 3600),
    elevation=int(forecast_response.Elevation())
)

# fill datetime column
forecast_tm2.fill_datetime_column(year=int(forecast_df.date.dt.year[0]))

tmy2_data = {
    'year': forecast_df.date.dt.year.astype(str).str[-2:].to_list(),  # list of years, with format YY
    'month': forecast_df.date.dt.month.astype(str).str.zfill(2).to_list(),  # list of months, with format MM
    'day': forecast_df.date.dt.day.astype(str).str.zfill(2).to_list(),  # list of days, with format DD
    'hour': forecast_df.date.dt.hour.astype(str).str.zfill(2).to_list(),  # list of hours, with format hh
}

for _varnames in INTERFACE:
    tmy2_data[_varnames[1]] = forecast_df[_varnames[0]].to_list()

first_hour = hour_of_year(
    year=int(tmy2_data['year'][0]),
    month=int(tmy2_data['month'][0]),
    day=int(tmy2_data['day'][0]),
    hour=int(tmy2_data['hour'][0]))

forecast_tm2.write(tmy2_data, start=first_hour)
# tm2.print()
forecast_tm2.export('test_forecast.tm2')

# endregion

# region HISTORICAL

# initialize tmy2 conversion
historical_tm2 = TMY2(
    lat=historical_response.Latitude(),
    long=historical_response.Longitude(),
    time_zone=historical_response.UtcOffsetSeconds() / 3600,
    elevation=int(historical_response.Elevation())
)

# fill datetime column
historical_tm2.fill_datetime_column(year)

tmy2_data = {
    'year': historical_df.date.dt.year.astype(str).str[-2:].to_list(),  # list of years, with format YY
    'month': historical_df.date.dt.month.astype(str).str.zfill(2).to_list(),  # list of months, with format MM
    'day': historical_df.date.dt.day.astype(str).str.zfill(2).to_list(),  # list of days, with format DD
    'hour': historical_df.date.dt.hour.astype(str).str.zfill(2).to_list(),  # list of hours, with format hh
}

for _varnames in INTERFACE:
    tmy2_data[_varnames[1]] = historical_df[_varnames[0]].to_list()

historical_tm2.write(tmy2_data)
# tm2.print()
historical_tm2.export('test_historical.tm2')

# endregion
