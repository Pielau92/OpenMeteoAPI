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


def print_response(response) -> None:
    """Print OpenMeteo API response.

    :param response: response from OpenMeteo API
    """

    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")


def get_hourly_values(response, variables: list[str]) -> dict:
    """Get hourly values from OpenMeteo API response.

    :param response: response from OpenMeteo API
    :param list variables: list of variables passed to the OpenMeteo API
    :return: hourly data as dict
    """

    hourly = response.Hourly()

    # create date column
    time_data = pd.date_range(
        start=pd.to_datetime(hourly.Time() + response.UtcOffsetSeconds(), unit="s", utc=True, ),
        end=pd.to_datetime(hourly.TimeEnd() + response.UtcOffsetSeconds(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left")
    hourly_data = {"date": time_data}

    # save hourly data into dictionary
    for index, variable in enumerate(variables):
        hourly_data[variable] = hourly.Variables(index).ValuesAsNumpy()

    return hourly_data


def hour_of_year(year: int, month: int, day: int, hour: int) -> int:
    """Return hour of year (from 0 to 8760) of a specified datetime.

    :param int year: year
    :param int month: month
    :param int day: day
    :param int hour: hour
    :return: hour of year (from 0 to 8760)
    """

    beginning_of_year = datetime.datetime(year, month=1, day=1, hour=1)
    date = datetime.datetime(year=year, month=month, day=day, hour=hour)
    return int((date - beginning_of_year).total_seconds() // 3600) + 1


def request_historical_data(client, params: dict, year: int):
    """Send request for historical data to OpenMeteo API.

    :param client: OpenMeteo API
    :param dict params: parameters (see OpenMeteo API doc)
    :param int year: year of requested historical dataset
    :return: OpenMeteo API response
    """

    # add start and end date of historical dataset
    params = params | {"start_date": f"{year}-01-01", "end_date": f"{year}-12-31"}

    # get response
    responses = client.weather_api(URL_historical, params=params)
    response = responses[0]  # process first location (add a for-loop for multiple locations or weather models)
    print_response(response)

    return response


def request_forecast_data(client, params: dict):
    """Send request for forecast data to OpenMeteo API.

    :param client: OpenMeteo API
    :param dict params: parameters (see OpenMeteo API doc)
    :return: OpenMeteo API response
    """

    # get response
    responses = client.weather_api(URL_forecast, params=params)
    response = responses[0]  # process first location (add a for-loop for multiple locations or weather models)
    print_response(response)

    return response
