# code generated and modified from https://open-meteo.com/en/docs

from ConvertToTM2.convert import TMY2
from openmeteo_api import setup_client, print_response, get_hourly_values, hour_of_year

import pandas as pd

URL = "https://api.open-meteo.com/v1/forecast"  # API url

# interface between OpenMeteo and tmy2 format (corresponding variable names as tuples)
interface = [
    ("temperature_2m", 'dry_bulb_temp'),
    ("relative_humidity_2m", 'rel_hum'),
    ("dew_point_2m", 'dew_point_temp'),
    ("rain", 'precipitable_water'),
    ("visibility", 'visibility'),
    ("cloud_cover", 'total_sky_cover'),
    ("surface_pressure", 'atmos_pressure'),
    ("wind_speed_10m", 'wind_speed'),
    ("wind_direction_10m", 'wind_dir'),
    ("diffuse_radiation", 'diff_hor_rad'),
    ("direct_radiation", 'dir_norm_rad'),
]

# list of variables packed in request to OpenMeteo
openmeteo_variables = [varnames[0] for varnames in interface]

# API request parameters
params = {
    "latitude": 48.2085,
    "longitude": 16.3721,
    "hourly": openmeteo_variables,
    "timezone": "auto"
}

# set up client, send request and receive response
openmeteo = setup_client()
responses = openmeteo.weather_api(URL, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print_response(response)

# extract hourly data
hourly_data = get_hourly_values(response, openmeteo_variables)

# convert dictionary into pandas DataFrame
hourly_dataframe = pd.DataFrame(hourly_data)
# print(hourly_dataframe)

tmy2_data = {
    'year': hourly_dataframe.date.dt.year.astype(str).str[-2:].to_list(),  # list of years, with format YY
    'month': hourly_dataframe.date.dt.month.astype(str).str.zfill(2).to_list(),  # list of months, with format MM
    'day': hourly_dataframe.date.dt.day.astype(str).str.zfill(2).to_list(),  # list of days, with format DD
    'hour': hourly_dataframe.date.dt.hour.astype(str).str.zfill(2).to_list(),  # list of hours, with format hh
}

for _varnames in interface:
    tmy2_data[_varnames[1]] = hourly_dataframe[_varnames[0]].to_list()

first_hour = hour_of_year(
    year=int(tmy2_data['year'][0]),
    month=int(tmy2_data['month'][0]),
    day=int(tmy2_data['day'][0]),
    hour=int(tmy2_data['hour'][0]))

tm2 = TMY2(params['latitude'], params['longitude'], time_zone=1)

year = int(hourly_dataframe.date.dt.year[0])
tm2.fill_datetime_column(year)
tm2.write(tmy2_data, start=first_hour)
tm2.print()
tm2.export('test.tm2')

pass
