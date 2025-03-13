from ConvertToTM2.tmy2format import HEADER_ELEMENTS_POS, DATA_ELEMENTS_POS


class TMY2:
    def __init__(self, length=8760):
        self.length = length
        self.header = Line(HEADER_ELEMENTS_POS, line_len=59)
        self.lines = [Line(DATA_ELEMENTS_POS, line_len=142) for _ in range(self.length)]

    def write(self, data):

        for line_index in range(self.length):
            values = {}
            for key in data:
                values.update({key: data[key][line_index]})
            self.lines[line_index].set_values(values)

    def print(self):
        for line in self.lines:
            print("".join(line.line))


class Line:
    def __init__(self, file_format, line_len):
        self.line = list(' ' * line_len)
        self.format = file_format

    def set_values(self, values):
        for key in values:
            self.set_value(key, values[key])

    def set_value(self, parameter, value):
        start_pos = self.format[parameter]['value'][0] - 1
        end_pos = self.format[parameter]['value'][1]
        self.line[start_pos:end_pos] = str(value).ljust(end_pos - start_pos)

