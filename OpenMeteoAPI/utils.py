import datetime


def get_lat_long_minutes(lat: float, long: float) -> (int, int):
    """Get latitude/longitude minutes from float latitude/longitude values.

    :param float lat: latitude
    :param float long: longitude
    :return:
        - lat_min - latitude minutes
        - long_min - longitude minutes
    """

    lat_int = int(lat)
    long_int = int(long)
    lat_min = int((lat - lat_int) * 60)
    long_min = int((long - long_int) * 60)

    return lat_min, long_min


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


def is_leap_year(year: int) -> bool:
    """Check if the year is a leap year."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
