from ConvertToTM2.convert import TMY2
from ConvertToTM2.tmy2format import OPENMETEO_MAPPING
from openmeteo_api import OpenMeteoClient
from OpenMeteoAPI.utils import *

client = OpenMeteoClient()

# list of variables packed in OpenMeteo request
openmeteo_variables = list(OPENMETEO_MAPPING.keys())

# request parameters
params = {
    "latitude": 48.2085,
    "longitude": 16.3721,
    "hourly": openmeteo_variables,
    "timezone": "auto",
}

this_year: int = datetime.date.today().year
from_year: int = 2022
years = list(range(from_year, this_year + 1))

# get responses from API requests
"""due to a delay the past day cannot be requested through historical weather API, use the forecast API with the
'past_days' parameter instead"""

historical_responses = dict()
for _year in years:
    historical_responses[str(_year)] = client.request_historical_data(params | {'models': 'ecmwf_ifs'}, _year)

forecast_response = client.request_forecast_data(params | {'models': 'icon_eu', 'forecast_days': 16, 'past_days': 1})

# convert responses into DataFrames
historical_dfs = dict()
for key in historical_responses:
    _df = client.get_hourly_df(historical_responses[key], openmeteo_variables)

    # remove leap day during leap years
    if is_leap_year(int(key)):
        _df = _df[~((_df.date.dt.month == 2) & (_df.date.dt.day == 29))]

    historical_dfs[key] = _df

forecast_df = client.get_hourly_df(forecast_response, openmeteo_variables)
past_day_df = forecast_df[0:24].copy()  # forecast of past day
forecast_df = forecast_df[25:]

# export function
export = lambda df, response, path: TMY2().export_from_openmeteo_df(data=df,
                                                                    lat=response.Latitude(), long=response.Longitude(),
                                                                    time_zone=int(response.UtcOffsetSeconds() / 3600),
                                                                    elevation=int(response.Elevation()), path=path)

# export historical data
for key in historical_responses:
    export(historical_dfs[key], historical_responses[key], f'../data/historical{str(key)}.tm2')

# export forecast data
export(forecast_df, forecast_response, '../data/forecast.tm2')

# export forecast data of the past day
export(past_day_df, forecast_response, '../data/forecast_past_day.tm2')

# add units to headers
headers = ['date'] + [_varname + '_' + OPENMETEO_MAPPING[_varname]['unit'] for _varname in openmeteo_variables]

for key in historical_dfs:
    historical_dfs[key].columns = headers

forecast_df.columns = headers
past_day_df.columns = headers

# csv exports
for key in historical_dfs:
    historical_dfs[key].to_csv(f'../data/historical{str(key)}.csv')

forecast_df.to_csv('../data/forecast.csv')
past_day_df.to_csv('../data/past_day.csv')
