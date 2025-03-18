# code generated and modified from https://open-meteo.com/en/docs

import openmeteo_requests
import requests_cache
import datetime

import pandas as pd

from retry_requests import retry
from ConvertToTM2.convert import TMY2

URL = "https://api.open-meteo.com/v1/forecast"  # API url


def setup_client():
    """Set up the Open-Meteo API client with cache and retry on error."""
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)


def print_response(response):
    """Print response."""
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")


def get_hourly_values(response, variables):
    """Process hourly data. The order of variables needs to be the same as requested."""
    hourly = response.Hourly()

    time_data = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left")

    # create hourly data dictionary
    hourly_data = {"date": time_data}

    for index, variable in enumerate(variables):
        hourly_data[variable] = hourly.Variables(index).ValuesAsNumpy()

    return hourly_data


def hour_of_year(year, month, day, hour):
    beginning_of_year = datetime.datetime(year, month=1, day=1, hour=1)
    date = datetime.datetime(year=year, month=month, day=day, hour=hour)
    return int((date - beginning_of_year).total_seconds() // 3600)


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

openmeteo_variables = [varnames[0] for varnames in interface]
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
tm2.write(tmy2_data, start=first_hour)
tm2.print()
tm2.export('test.tm2')

pass
