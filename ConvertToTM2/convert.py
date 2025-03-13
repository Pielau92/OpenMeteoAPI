from ConvertToTM2.tmy2format import HEADER_ELEMENTS_POS, DATA_ELEMENTS_POS


class TMY2:
    def __init__(self, length=8760):
        self.length = length
        self.header = Record(HEADER_ELEMENTS_POS, line_len=59)
        self.records = [Record(DATA_ELEMENTS_POS, line_len=142) for _ in range(self.length)]

    def write(self, data, start=0):
        data_len = len(data['hour'])
        for line_index in range(data_len):
            values = {}
            for key in data:
                values.update({key: data[key][line_index]})
            self.records[start + line_index].set_values(values)

    def print(self):
        for line in self.records:
            print("".join(line.data))


class Record:
    def __init__(self, file_format, line_len):
        self.data = list(' ' * line_len)
        self.format = file_format

    def set_values(self, values):
        for key in values:
            self.set_value(key, values[key])

    def set_value(self, parameter, value):
        start_pos = self.format[parameter]['value'][0] - 1
        end_pos = self.format[parameter]['value'][1]
        entry_len = end_pos - start_pos

        if 'factor' in self.format[parameter].keys():
            value = value / self.format[parameter]['factor']

        self.data[start_pos:end_pos] = f"{int(value):0{entry_len}d}"
