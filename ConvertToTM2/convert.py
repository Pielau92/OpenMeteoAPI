from ConvertToTM2.tmy2format import HEADER_ELEMENTS_POS, DATA_ELEMENTS_POS
from OpenMeteoAPI.utils import *

import datetime


class TMY2:
    def __init__(self, lat: float, long: float, time_zone: int, elevation: int, length: int = 8760) -> None:
        """Initialize tmy2 conversion.

        For more information about the tmy2 format, see "The User's Manual for TMY2s" under
        https://www.nrel.gov/docs/legosti/old/7668.pdf.

        :param int length: length of tm2 file (number of records, typically 1 record per hour for a year, so 8760)
        """
        self.length = length
        self.header = HeaderRecord(lat=lat, long=long, time_zone=time_zone, elevation=elevation)
        self.header.update()
        self.records = [DataRecord() for _ in range(self.length)]

    def write(self, data: dict, start: int = 0) -> None:
        """Write weather dataset into records.

        TMY2 format does not support leap year, therfore they habe to be removed beforehand.

        :param dict data: dict with parameter as key and data as list
        :param int start: starting position of the dataset within the tm2 file (0-8759)
        """

        data_len: int = len(data['hour'])

        for data_index in range(data_len):

            values = {}  # key-value pairs with data from current hour
            for key in data:
                values.update({key: data[key][data_index]})

            # set values from all key-value pairs individually
            self.records[start + data_index].set_values(values)

    def print(self) -> None:
        """Print all records."""

        print("".join(self.header.data))
        for record in self.records:
            print("".join(record.data))

    def export(self, path: str) -> None:
        """Export all records to designated path as tm2 file.

        :param str path: output path, to receive a tm2 file, the file extension should be .tm2
        """

        with open(path, 'w') as f:
            f.write("".join(self.header.data))  # write header
            for record in self.records:
                f.write('\n')  # new line
                f.write("".join(record.data))  # write record

    def fill_datetime_column(self, year: int) -> None:
        """Fill the datetime column.

        :param int year: year of the dataset
        """

        date = datetime.datetime(year, month=1, day=1, hour=0)
        dt = datetime.timedelta(hours=1)

        for record in self.records:
            record.set_values(values={
                'year': int(repr(date.year)[-2:]),
                'month': date.month,
                'day': date.day,
                'hour': date.hour,
            })
            date += dt


class Record:
    def __init__(self, file_format: dict, line_len: int) -> None:
        """Initialize record.

        Regarding the tmy2 (Typical Meteorological Years) format, the term "record" defines a single line. The first
        record is reserved for the header, all others a data records in hourly resolution with multiple sensor entries.

        :param dict file_format: tmy2 format information containing the positions of individual elements within a record
        :param int line_len: length of the record (number of characters)
        """

        self.data = list(' ' * line_len)  # data consisting of a list of characters
        self.format = file_format  # tmy2 format information about header and data element, as dict

    def set_values(self, values: dict) -> None:
        """Writes multiple key-value pairs into the record.

        Accepts a dict of key-value pairs (key must correspond to the name of an element in the tmy2 format) and writes
        the value at the designated position inside the record.

        :param dict values: key-value pairs to be written inside the record
        """

        for key in values:
            self.set_value(key, values[key])

    def set_value(self, key: str, value: int | float) -> None:
        """Writes a single key-value pair inside the record.

        :param str key: key which corresponds to the name of an element in the tmy2 format
        :param int | float value: value to be written inside the record
        """

        # start and end of the position designated to the element corresponding to the passed key
        start_pos = self.format[key]['value'][0] - 1
        end_pos = self.format[key]['value'][1]

        entry_len = end_pos - start_pos  # length of entry

        # if the element has a conversion factor, perform conversion
        if 'factor' in self.format[key].keys():
            value = value / self.format[key]['factor']

        # write entry into record - right-aligned and with 0s at unused digits
        self.data[start_pos:end_pos] = f"{int(value):0{entry_len}d}"


class HeaderRecord(Record):
    def __init__(self, lat: float, long: float, time_zone: int,
                 wban: str = '00000', city: str = 'unknown', state: str = 'ZZ', elevation: int = 0) -> None:
        """Initialize header record."""

        # initialize as header record
        super().__init__(HEADER_ELEMENTS_POS, 59)

        self.wban = wban
        self.city = city.ljust(22)
        self.state = state
        self.timezone = str(int(time_zone)).rjust(3)

        lat_min, long_min = get_lat_long_minutes(lat, long)
        self.latitude = ('N'
                         + f' {int(lat):02d}'  # degrees
                         + f' {int(lat_min):02d}'  # minutes
                         )
        self.longitude = (('W', 'E')[long > 0]
                          + f' {int(long):02d}'  # degrees
                          + f' {int(long_min):02d}'  # minutes
                          )

        self.elevation = f'{elevation:03d}'

    def update(self) -> None:
        """Updates header record according to attribute values of the instance."""

        for key in self.format:
            # start and end of the position designated to the element corresponding to the passed key
            start_pos = self.format[key]['value'][0] - 1
            end_pos = self.format[key]['value'][1]

            entry_len = end_pos - start_pos  # length of entry

            # write entry into record - right-aligned and with 0s at unused digits
            self.data[start_pos:end_pos] = getattr(self, key)


class DataRecord(Record):
    def __init__(self):
        """Initialize data record."""

        # initialize as data record
        super().__init__(DATA_ELEMENTS_POS, 142)

        # define flags
        self.source_flag = '?'
        self.uncertainty_flag = '0'

        self.reset()  # fill record with "missing data" values

    def reset(self) -> None:
        """Reset data record.

        Fills record with "missing data" values, "unknown" source flag and "not applicable" uncertainty flag.
        """

        for key in self.format:
            if key in ['year', 'month', 'day', 'hour']:
                continue  # do not initialize time data

            # create "missing data" entry
            start_pos = self.format[key]['value'][0] - 1  # start...
            end_pos = self.format[key]['value'][
                1]  # ...and end of the position designated to the value of the element corresponding to the key
            entry_len = end_pos - start_pos  # length of entry
            missing_data_entry = '9' * entry_len

            # write entry into record - right-aligned and with leading zeros
            self.data[start_pos:end_pos] = missing_data_entry

            # set source flag
            if 'source_flag' in self.format[key].keys():
                self.data[self.format[key]['source_flag'] - 1] = self.source_flag

            # set uncertainty flag
            if 'uncertainty_flag' in self.format[key].keys():
                self.data[self.format[key]['uncertainty_flag'] - 1] = self.uncertainty_flag
