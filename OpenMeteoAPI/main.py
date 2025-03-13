# code generated and modified from https://open-meteo.com/en/docs

import openmeteo_requests
import requests_cache

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


# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
variables = ["temperature_2m", "relative_humidity_2m"]
params = {
    "latitude": 48.2085,
    "longitude": 16.3721,
    "hourly": variables,
    "timezone": "auto"
}

# set up client, send request and receive response
openmeteo = setup_client()
responses = openmeteo.weather_api(URL, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print_response(response)

# extract hourly data
hourly_data = get_hourly_values(response, variables)

# convert dictionary into pandas DataFrame
hourly_dataframe = pd.DataFrame(hourly_data)
print(hourly_dataframe)

tmy2_data = {
    'year': hourly_dataframe.date.dt.year.astype(str).str[-2:].to_list(),  # list of years, with format YY
    'month': hourly_dataframe.date.dt.month.astype(str).str.zfill(2).to_list(),  # list of months, with format MM
    'day': hourly_dataframe.date.dt.day.astype(str).str.zfill(2).to_list(),  # list of days, with format DD
    'hour': hourly_dataframe.date.dt.hour.astype(str).str.zfill(2).to_list(),  # list of hours, with format hh
    'dry_bulb_temp': hourly_dataframe['temperature_2m'].to_list(),
    'rel_hum': hourly_dataframe['relative_humidity_2m'].to_list()
}

tm2 = TMY2(length=200)
tm2.write(tmy2_data, 10)
tm2.print()

pass
