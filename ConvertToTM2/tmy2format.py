"""tmy2 format information issued from "The User's Manual for TMY2s"
(https://www.nrel.gov/docs/legosti/old/7668.pdf)."""

"""Position of each element inside the header.
    single value = single position
    tuple = position from...to (example: (1, 2) = from position 1 to 2 included)"""
HEADER_ELEMENTS_POS = {
    'wban': {'value': (2, 6)},
    'city': {'value': (8, 29)},
    'state': {'value': (31, 32)},
    'timezone': {'value': (34, 36)},

    'latitude': {
        'value': (38, 44),
        'north': 38,
        'degrees': (40, 41),
        'minutes': (43, 44),
    },

    'longitude': {
        'value': (46, 53),
        'north': 46,
        'degrees': (48, 50),
        'minutes': (52, 53),
    },

    # NOTE: in source material the field position for elevation is 56-59, seems to be an error though
    'elevation': {'value': (57, 59)}
}

"""Position of each element inside a record.
    single value = single position
    tuple = position from...to (example: (1, 2) = from position 1 to 2 included)"""
DATA_ELEMENTS_POS = {
    # local standard time
    'year': {'value': (2, 3)},
    'month': {'value': (4, 5)},
    'day': {'value': (6, 7)},
    'hour': {'value': (8, 9)},

    # extraterrestrial horizontal radiation [W/m²]
    'et_hor_rad': {'value': (10, 13)},

    # extraterrestrial direct normal radiation [W/m²]
    'et_dir_norm_rad': {'value': (14, 17)},

    # global horizontal radiation [W/m²]
    'global_hor_rad': {
        'value': (18, 21),
        'source_flag': 22,
        'uncertainty_flag': 23
    },

    # direct normal radiation [W/m²]
    'dir_norm_rad': {
        'value': (24, 27),
        'source_flag': 28,
        'uncertainty_flag': 29
    },

    # diffuse horizontal radiation [W/m²]
    'diff_hor_rad': {
        'value': (30, 33),
        'source_flag': 34,
        'uncertainty_flag': 35,
    },

    # global horizontal illuminance [100 lux]
    'global_hor_ill': {
        'value': (36, 39),
        'factor': 100,
        'source_flag': 40,
        'uncertainty_flag': 41,
    },

    # direct normal illuminance [100 lux]
    'dir_norm_illuminance': {
        'value': (42, 45),
        'factor': 100,
        'source_flag': 46,
        'uncertainty_flag': 47,
    },

    # diffuse horizontal illuminance [100 lux]
    'diff_hor_illuminance': {
        'value': (48, 51),
        'factor': 100,
        'source_flag': 52,
        'uncertainty_flag': 53,
    },

    # zenith luminance [10 Cd/m²]
    'zenith_illuminance': {
        'value': (54, 57),
        'factor': 10,
        'source_flag': 58,
        'uncertainty_flag': 59,
    },

    # total sky cover [10 %]
    'total_sky_cover': {
        'value': (60, 61),
        'factor': 10,
        'source_flag': 62,
        'uncertainty_flag': 63,
    },

    # opaque sky cover [10 %]
    'opaque_sky_cover': {
        'value': (64, 65),
        'factor': 10,
        'source_flag': 66,
        'uncertainty_flag': 67,
    },

    # dry bulb temperature [0.1 °C]
    'dry_bulb_temp': {
        'value': (68, 71),
        'factor': 0.1,
        'source_flag': 72,
        'uncertainty_flag': 73,
    },

    # dew point temperature [0.1 °C]
    'dew_point_temp': {
        'value': (74, 77),
        'factor': 0.1,
        'source_flag': 78,
        'uncertainty_flag': 79,
    },

    # relative humidity [%]
    'rel_hum': {
        'value': (80, 82),
        'source_flag': 83,
        'uncertainty_flag': 84,
    },

    # atmospheric pressure [mbar]
    'atmos_pressure': {
        'value': (85, 88),
        'source_flag': 89,
        'uncertainty_flag': 90,
    },

    # wind direction [degree], N=0
    'wind_dir': {
        'value': (91, 93),
        'source_flag': 94,
        'uncertainty_flag': 95,
    },

    # wind speed [0.1 m/s]
    'wind_speed': {
        'value': (96, 98),
        'factor': 0.1,
        'source_flag': 99,
        'uncertainty_flag': 100,
    },

    # visibility [0.1 km]
    'visibility': {
        'value': (101, 104),
        'factor': 0.1,
        'source_flag': 105,
        'uncertainty_flag': 106,
    },

    # ceiling height [m]
    'ceiling_height': {
        'value': (107, 111),
        'source_flag': 112,
        'uncertainty_flag': 113,
    },

    # present weather
    'present_weather': {'value': (114, 123)},

    # precipitable_water [mm]
    'precipitable_water': {
        'value': (124, 126),
        'source_flag': 127,
        'uncertainty_flag': 128,
    },

    # aerosol optical depth [0.001 day]
    'aerosol_optical_depth': {
        'value': (129, 131),
        'source_flag': 132,
        'uncertainty_flag': 133,
    },

    # snow depth [cm]
    'snow_depth': {
        'value': (134, 136),
        'source_flag': 137,
        'uncertainty_flag': 138,
    },

    # days since last snowfall [day]
    'days_since_snowfall': {
        'value': (139, 140),
        'source_flag': 141,
        'uncertainty_flag': 142,
    }
}

# Mapping between tmy2/OpenMeteo variable names
OPENMETEO_MAPPING = {
    'temperature_2m': {
        'tm2_varname': 'dry_bulb_temp',
        'unit': '°C',
    },
    'relative_humidity_2m': {
        'tm2_varname': 'rel_hum',
        'unit': '%'
    },
    'dew_point_2m': {
        'tm2_varname': 'dew_point_temp',
        'unit': '°C'
    },
    'rain': {
        'tm2_varname': 'precipitable_water',
        'unit': 'mm'
    },
    'cloud_cover': {
        'tm2_varname': 'total_sky_cover',
        'unit': '%'
    },
    'surface_pressure': {
        'tm2_varname': 'atmos_pressure',
        'unit': 'hPa'
    },
    'wind_speed_10m': {
        'tm2_varname': 'wind_speed',
        'unit': 'km/h'
    },
    'wind_direction_10m': {
        'tm2_varname': 'wind_dir',
        'unit': '°'
    },
    'diffuse_radiation': {
        'tm2_varname': 'diff_hor_rad',
        'unit': 'W/m²'
    },
    'direct_radiation': {
        'tm2_varname': 'dir_norm_rad',
        'unit': 'W/m²'
    }
}
