from ConvertToTM2.convert import TMY2
from ConvertToTM2.tmy2format import OPENMETEO_MAPPING
from openmeteo_api import OpenMeteoClient
from OpenMeteoAPI.utils import *

import pandas as pd

client = OpenMeteoClient()

# list of variables packed in OpenMeteo request
openmeteo_variables = list(OPENMETEO_MAPPING.keys())

latitude = 48.2085
longitude = 16.3721
this_year = datetime.date.today().year  # year of historical dataset
last_year = datetime.date.today().year - 1  # year of historical dataset

params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": openmeteo_variables,
    "timezone": "auto",
    "models": ["icon_global", "icon_eu"],
}

# send API requests
"""due to a delay the past day cannot be requested through historical weather API, use the forecast API with the
'past_days' parameter instead"""
this_year_response = client.request_historical_data(params, this_year)
last_year_response = client.request_historical_data(params, last_year)
forecast_response = client.request_forecast_data(params | {'forecast_days': 16, 'past_days': 1})

# print responses
for _response in [this_year_response, last_year_response, forecast_response]:
    client.print_response(_response)


# convert response into dictionary
this_year_df = client.get_hourly_df(this_year_response, openmeteo_variables)
last_year_df = client.get_hourly_df(last_year_response, openmeteo_variables)
forecast_df = client.get_hourly_df(forecast_response, openmeteo_variables)
past_day_df = forecast_df[0:24]  # take only the past day

# remove leap day during leap years
if is_leap_year(this_year):
    this_year_df = this_year_df[~((this_year_df.date.dt.month == 2) & (this_year_df.date.dt.day == 29))]
if is_leap_year(last_year):
    last_year_df = last_year_df[~((last_year_df.date.dt.month == 2) & (last_year_df.date.dt.day == 29))]
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

# collect tmy2 data
tmy2_data = {
    'year': forecast_df.date.dt.year.astype(str).str[-2:].astype(int).to_list(),  # list of years, with format YY
    'month': forecast_df.date.dt.month.astype(str).str.zfill(2).astype(int).to_list(),  # list of months, with format MM
    'day': forecast_df.date.dt.day.astype(str).str.zfill(2).astype(int).to_list(),  # list of days, with format DD
    'hour': forecast_df.date.dt.hour.astype(str).str.zfill(2).astype(int).to_list(),  # list of hours, with format hh
}
for _key in OPENMETEO_MAPPING.keys():
    tmy2_data[OPENMETEO_MAPPING[_key]['tm2_varname']] = forecast_df[_key].to_list()

# determine at which hour of the year the data begins
first_hour = hour_of_year(
    year=int(tmy2_data['year'][0]),
    month=int(tmy2_data['month'][0]),
    day=int(tmy2_data['day'][0]),
    hour=int(tmy2_data['hour'][0]))

# write tmy2 data into tmy2 records
forecast_tm2.write(tmy2_data, start=first_hour)
# tm2.print()

forecast_tm2.export('../data/forecast.tm2')

# endregion

# region HISTORICAL (THIS YEAR)

# initialize tmy2 conversion
this_year_tm2 = TMY2(
    lat=this_year_response.Latitude(),
    long=this_year_response.Longitude(),
    time_zone=this_year_response.UtcOffsetSeconds() / 3600,
    elevation=int(this_year_response.Elevation())
)

# fill datetime column
this_year_tm2.fill_datetime_column(this_year)

# collect tmy2 data
tmy2_data = {
    'year': this_year_df.date.dt.year.astype(str).str[-2:].astype(int).to_list(),  # list of years, with format YY
    'month': this_year_df.date.dt.month.astype(str).str.zfill(2).astype(int).to_list(),
    # list of months, with format MM
    'day': this_year_df.date.dt.day.astype(str).str.zfill(2).astype(int).to_list(),  # list of days, with format DD
    'hour': this_year_df.date.dt.hour.astype(str).str.zfill(2).astype(int).to_list(),  # list of hours, with format hh
}
for _key in OPENMETEO_MAPPING.keys():
    tmy2_data[OPENMETEO_MAPPING[_key]['tm2_varname']] = this_year_df[_key].to_list()

# write tmy2 data into tmy2 records
this_year_tm2.write(tmy2_data)
# tm2.print()

this_year_tm2.export(f'../data/year{this_year}.tm2')

# endregion

# region HISTORICAL (LAST YEAR)

# initialize tmy2 conversion
last_year_tm2 = TMY2(
    lat=last_year_response.Latitude(),
    long=last_year_response.Longitude(),
    time_zone=last_year_response.UtcOffsetSeconds() / 3600,
    elevation=int(last_year_response.Elevation())
)

# fill datetime column
last_year_tm2.fill_datetime_column(last_year)

# collect tmy2 data
tmy2_data = {
    'year': last_year_df.date.dt.year.astype(str).str[-2:].astype(int).to_list(),  # list of years, with format YY
    'month': last_year_df.date.dt.month.astype(str).str.zfill(2).astype(int).to_list(),
    # list of months, with format MM
    'day': last_year_df.date.dt.day.astype(str).str.zfill(2).astype(int).to_list(),  # list of days, with format DD
    'hour': last_year_df.date.dt.hour.astype(str).str.zfill(2).astype(int).to_list(),  # list of hours, with format hh
}
for _key in OPENMETEO_MAPPING.keys():
    tmy2_data[OPENMETEO_MAPPING[_key]['tm2_varname']] = last_year_df[_key].to_list()

# write tmy2 data into tmy2 records
last_year_tm2.write(tmy2_data)
# tm2.print()

last_year_tm2.export(f'../data/year{last_year}.tm2')

# endregion

# region PAST DAY

# initialize tmy2 conversion
past_day_tm2 = TMY2(
    lat=past_day_response.Latitude(),
    long=past_day_response.Longitude(),
    time_zone=int(past_day_response.UtcOffsetSeconds() / 3600),
    elevation=int(past_day_response.Elevation())
)

# fill datetime column
past_day_tm2.fill_datetime_column(year=int(past_day_df.date.dt.year[0]))

# collect tmy2 data
tmy2_data = {
    'year': past_day_df.date.dt.year.astype(str).str[-2:].astype(int).to_list(),  # list of years, with format YY
    'month': past_day_df.date.dt.month.astype(str).str.zfill(2).astype(int).to_list(),  # list of months, with format MM
    'day': past_day_df.date.dt.day.astype(str).str.zfill(2).astype(int).to_list(),  # list of days, with format DD
    'hour': past_day_df.date.dt.hour.astype(str).str.zfill(2).astype(int).to_list(),  # list of hours, with format hh
}
for _key in OPENMETEO_MAPPING.keys():
    tmy2_data[OPENMETEO_MAPPING[_key]['tm2_varname']] = past_day_df[_key].to_list()

# determine at which hour of the year the data begins
first_hour = hour_of_year(
    year=int(tmy2_data['year'][0]),
    month=int(tmy2_data['month'][0]),
    day=int(tmy2_data['day'][0]),
    hour=int(tmy2_data['hour'][0]))

# write tmy2 data into tmy2 records
past_day_tm2.write(tmy2_data, start=first_hour)
# tm2.print()

past_day_tm2.export('../data/past_day.tm2')

# endregion

# add units to headers
headers = ['date']
headers += [_varname + '_' + OPENMETEO_MAPPING[_varname]['unit'] for _varname in openmeteo_variables]
this_year_df.columns = headers
last_year_df.columns = headers
forecast_df.columns = headers
past_day_df.columns = headers

# csv exports
this_year_df.to_csv(f'../data/year{this_year}.csv')
last_year_df.to_csv(f'../data/year{last_year}.csv')
forecast_df.to_csv('../data/forecast.csv')
past_day_df.to_csv('../data/past_day.csv')
