# code generated and modified from https://open-meteo.com/en/docs

import openmeteo_requests
import requests_cache
import datetime

import pandas as pd

from retry_requests import retry

# API URLs
URL_forecast = "https://api.open-meteo.com/v1/forecast"
URL_historical = "https://archive-api.open-meteo.com/v1/archive"


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
        start=pd.to_datetime(hourly.Time() + response.UtcOffsetSeconds(), unit="s", utc=True, ),
        end=pd.to_datetime(hourly.TimeEnd() + response.UtcOffsetSeconds(), unit="s", utc=True),
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
    return int((date - beginning_of_year).total_seconds() // 3600) + 1


def request_historical_data(client, params, year):
    # add start and end date of historical dataset
    params = params | {"start_date": f"{year}-01-01", "end_date": f"{year}-12-31"}

    # get response
    responses = client.weather_api(URL_historical, params=params)
    response = responses[0]  # process first location (add a for-loop for multiple locations or weather models)
    print_response(response)

    return response


def request_forecast_data(client, params):
    # get response
    responses = client.weather_api(URL_forecast, params=params)
    response = responses[0]  # process first location (add a for-loop for multiple locations or weather models)
    print_response(response)

    return response
