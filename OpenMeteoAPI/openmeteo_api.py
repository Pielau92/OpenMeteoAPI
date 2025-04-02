# code generated and modified from https://open-meteo.com/en/docs
import datetime
import requests_cache

import pandas as pd

from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse
from openmeteo_requests import Client
from retry_requests import retry

# API URLs
URL_forecast = "https://api.open-meteo.com/v1/forecast"
URL_historical = "https://archive-api.open-meteo.com/v1/archive"


class OpenMeteoClient(Client):
    """OpenMeteo API Client."""

    def __init__(self):
        """Set up the Open-Meteo API client with cache and retry on error."""
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        super().__init__(session=retry_session)

    def request_historical_data(self, params: dict, year: int) -> WeatherApiResponse:
        """Send request for historical data of a given year to OpenMeteo API.

        :param dict params: parameters (see OpenMeteo API doc)
        :param int year: year of requested historical dataset
        :return: OpenMeteo API response
        """

        # if data from current year is requested, limit to current day instead of whole year
        if year == datetime.date.today().year:
            end_date = str(datetime.date.today())
        else:
            end_date = f'{year}-12-31'

        # add start and end date of historical dataset
        params = params | {'start_date': f'{year}-01-01', 'end_date': end_date}

        # get response
        responses = self.weather_api(URL_historical, params=params)
        response = responses[0]

        return response

    def request_forecast_data(self, params: dict) -> WeatherApiResponse:
        """Send request for forecast data to OpenMeteo API.

        :param dict params: parameters (see OpenMeteo API doc)
        :return: OpenMeteo API response
        """

        # get response
        responses = self.weather_api(URL_forecast, params=params)
        response = responses[0]

        return response

    @staticmethod
    def print_response(response: WeatherApiResponse) -> None:
        """Print OpenMeteo API response.

        :param response: response from OpenMeteo API
        """

        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    @staticmethod
    def get_hourly_df(response: WeatherApiResponse, variables: list[str]) -> pd.DataFrame:
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

        return pd.DataFrame(hourly_data)
