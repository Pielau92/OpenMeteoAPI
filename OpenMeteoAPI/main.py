# code generated and modified from https://open-meteo.com/en/docs

from ConvertToTM2.convert import TMY2
from openmeteo_api import setup_client, print_response, get_hourly_values, hour_of_year, request_data

import pandas as pd

# API URLs
URL_forecast = "https://api.open-meteo.com/v1/forecast"
URL_historical = "https://archive-api.open-meteo.com/v1/archive"

# interface between OpenMeteo and tmy2 format (corresponding variable names as tuples)
interface = [
    ("temperature_2m", 'dry_bulb_temp'),
    ("relative_humidity_2m", 'rel_hum'),
    ("dew_point_2m", 'dew_point_temp'),
    ("rain", 'precipitable_water'),
    # ("visibility", 'visibility'),
    ("cloud_cover", 'total_sky_cover'),
    ("surface_pressure", 'atmos_pressure'),
    ("wind_speed_10m", 'wind_speed'),
    ("wind_direction_10m", 'wind_dir'),
    ("diffuse_radiation", 'diff_hor_rad'),
    ("direct_radiation", 'dir_norm_rad'),
]

# list of variables packed in request to OpenMeteo
openmeteo_variables = [varnames[0] for varnames in interface]

latitude = 48.2085
longitude = 16.3721

forecast_data, forecast_response = request_data(URL_forecast, latitude, longitude, openmeteo_variables)
historical_data, historical_response = request_data(URL_historical, latitude, longitude, openmeteo_variables, 2023)

# region FORECAST

tmy2_data = {
    'year': forecast_data.date.dt.year.astype(str).str[-2:].to_list(),  # list of years, with format YY
    'month': forecast_data.date.dt.month.astype(str).str.zfill(2).to_list(),  # list of months, with format MM
    'day': forecast_data.date.dt.day.astype(str).str.zfill(2).to_list(),  # list of days, with format DD
    'hour': forecast_data.date.dt.hour.astype(str).str.zfill(2).to_list(),  # list of hours, with format hh
}

for _varnames in interface:
    tmy2_data[_varnames[1]] = forecast_data[_varnames[0]].to_list()

first_hour = hour_of_year(
    year=int(tmy2_data['year'][0]),
    month=int(tmy2_data['month'][0]),
    day=int(tmy2_data['day'][0]),
    hour=int(tmy2_data['hour'][0]))

tm2 = TMY2(lat=forecast_response.Latitude(), long=forecast_response.Longitude(), time_zone=forecast_response.UtcOffsetSeconds() / 360,
           elevation=int(forecast_response.Elevation()))

year = int(forecast_data.date.dt.year[0])
tm2.fill_datetime_column(year)
tm2.write(tmy2_data, start=first_hour)
# tm2.print()
tm2.export('test_forecast.tm2')

# endregion

# region HISTORICAL

tmy2_data = {
    'year': historical_data.date.dt.year.astype(str).str[-2:].to_list(),  # list of years, with format YY
    'month': historical_data.date.dt.month.astype(str).str.zfill(2).to_list(),  # list of months, with format MM
    'day': historical_data.date.dt.day.astype(str).str.zfill(2).to_list(),  # list of days, with format DD
    'hour': historical_data.date.dt.hour.astype(str).str.zfill(2).to_list(),  # list of hours, with format hh
}

for _varnames in interface:
    tmy2_data[_varnames[1]] = historical_data[_varnames[0]].to_list()

tm2 = TMY2(lat=historical_response.Latitude(), long=historical_response.Longitude(), time_zone=historical_response.UtcOffsetSeconds() / 360,
           elevation=int(historical_response.Elevation()))

year = int(historical_data.date.dt.year[0])
tm2.fill_datetime_column(year)
tm2.write(tmy2_data)
# tm2.print()
tm2.export('test_historical.tm2')

# endregion