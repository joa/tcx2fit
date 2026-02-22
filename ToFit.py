import struct
from datetime import datetime
import io

# Based on: https://github.com/SuperTaiyaki/fitconverter/blob/master/write_fit.py

# Default test data
laps = [(0, 966665266, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 60, 0, 4, 14)]

records = [
    [(966665266, 0, 0, 0, 0, 0, 0, 0, 0),
     (966665268, 0, 0, 0, 0, 0, 0, 0, 0)]
]

heart_rate_zones = [
    (0, 100),
    (1, 119),
    (2, 149),
    (3, 169),
    (4, 189),
    (5, 199),
]

event_start = [966665266, 0, 0, 1]
event_stop = [966665268, 0, 4, 0]


class file_id:
    def __init__(self, attr=None):
        if attr is None:
            attr = [966665266, 4, 118, 1, 1234567891]
        self.id = 0
        self.record_id = 0
        self.write_data = True
        self.fields = [
            (0, "enum", attr[1]),       # type: 4 = Activity
            (1, "uint16", attr[2]),     # manufacturer: 118 = WaterRower
            (2, "uint16", attr[3]),     # product
            (3, "uint32z", attr[4]),    # serial number
            (4, "uint32", attr[0]),     # time_created
        ]

    def output_byte(self):
        parts = write_field(self.id, self.fields, self.write_data, self.record_id)
        return parts[0] + parts[1]


class event:
    def __init__(self, attr=None):
        if attr is None:
            attr = [966665266, 0, 0, 0]
        self.id = 21
        self.record_id = 0
        self.write_data = True
        self.fields = [
            (253, "uint32", attr[0]),   # timestamp
            (0, "enum", attr[1]),       # event
            (1, "enum", attr[2]),       # event_type
            (3, "enum", attr[3]),       # timer_trigger
        ]

    def output_byte(self):
        parts = write_field(self.id, self.fields, self.write_data, self.record_id)
        return parts[0] + parts[1]


class user_profile:
    def __init__(self, attr=None):
        if attr is None:
            attr = [1, 30, 170, 700, 60, 200]
        self.id = 3
        self.record_id = 0
        self.write_data = True
        self.fields = [
            (1, "enum", attr[0]),       # gender
            (2, "uint8", attr[1]),      # age
            (3, "uint8", attr[2]),      # height
            (4, "uint16", attr[3]),     # weight
            (8, "uint8", attr[4]),      # resting_heart_rate
            (11, "uint8", attr[5]),     # default_max_heart_rate
        ]

    def output_byte(self):
        parts = write_field(self.id, self.fields, self.write_data, self.record_id)
        return parts[0] + parts[1]


class sport:
    def __init__(self, attr=None):
        if attr is None:
            attr = [4, 14]
        self.id = 12
        self.record_id = 0
        self.write_data = True
        self.fields = [
            (0, "enum", attr[0]),       # sport: Fitness Equipment
            (1, "enum", attr[1]),       # sub_sport: Indoor Rowing
        ]

    def output_byte(self):
        parts = write_field(self.id, self.fields, self.write_data, self.record_id)
        return parts[0] + parts[1]


class zones_target:
    def __init__(self, attr=None):
        if attr is None:
            attr = [199]
        self.id = 7
        self.record_id = 0
        self.write_data = True
        self.fields = [
            (1, "uint8", attr[0]),      # max_heart_rate
        ]

    def output_byte(self):
        parts = write_field(self.id, self.fields, self.write_data, self.record_id)
        return parts[0] + parts[1]


class hr_zone:
    def __init__(self, attr=None):
        if attr is None:
            attr = [0, 100]
        self.id = 8
        self.record_id = 0
        self.write_data = True
        self.fields = [
            (254, "uint16", attr[0]),   # message_index
            (1, "uint8", attr[1]),      # high_bpm
        ]

    def output_byte(self):
        return write_field(self.id, self.fields, self.write_data, self.record_id)


class activity:
    def __init__(self, attr=None):
        if attr is None:
            attr = [966665267, 1, 1]
        self.id = 34
        self.record_id = 0
        self.write_data = True
        self.fields = [
            (253, "uint32", attr[0]),   # timestamp
            (0, "uint32", attr[1]),     # total_timer_time
            (1, "uint16", attr[2]),     # num_sessions
        ]

    def output_byte(self):
        return write_field(self.id, self.fields, self.write_data, self.record_id)


class session:
    def __init__(self, attr=None):
        if attr is None:
            attr = [966665267, 966665266, 3, 4, 4, 14, 1, 1, 10, 206, 5, 15, 150, 200, 23, 30, 150, 300, 1, 294, 60, 10]
        self.id = 18
        self.record_id = 0
        self.write_data = True
        self.fields = [
            (253, "uint32", attr[0]),   # timestamp
            (2, "uint32", attr[1]),     # start_time
            (3, "sint32", attr[2]),     # start_position_lat
            (4, "sint32", attr[3]),     # start_position_long
            (5, "enum", attr[4]),       # sport
            (6, "enum", attr[5]),       # sub_sport
            (7, "uint32", attr[6]),     # total_elapsed_time
            (8, "uint32", attr[7]),     # total_timer_time
            (9, "uint32", attr[8]),     # total_distance
            (11, "uint16", attr[9]),    # total_calories
            (14, "uint16", attr[10]),   # avg_speed
            (15, "uint16", attr[11]),   # max_speed
            (16, "uint8", attr[12]),    # avg_heart_rate
            (17, "uint8", attr[13]),    # max_heart_rate
            (18, "uint8", attr[14]),    # avg_cadence
            (19, "uint8", attr[15]),    # max_cadence
            (20, "uint16", attr[16]),   # avg_power
            (21, "uint16", attr[17]),   # max_power
            (25, "uint16", 0),          # first_lap_index
            (26, "uint16", attr[18]),   # num_lap
            (48, "uint32", attr[19]),   # total_work
            (64, "uint8", attr[20]),    # min_heart_rate
            (10, "uint32", attr[21]),   # stroke_count
        ]

    def output_byte(self):
        return write_field(self.id, self.fields, self.write_data, self.record_id)


class lap:
    def __init__(self, attr=None):
        if attr is None:
            attr = [0, 966665266, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 14]
        self.id = 19
        self.record_id = 0
        self.write_data = True
        self.fields = [
            (253, "uint32", attr[1]),   # timestamp
            (2, "uint32", attr[2]),     # start_time
            (3, "sint32", attr[3]),     # start_position_lat
            (4, "sint32", attr[4]),     # start_position_long
            (5, "sint32", attr[5]),     # end_position_lat
            (6, "sint32", attr[6]),     # end_position_long
            (7, "uint32", attr[7]),     # total_elapsed_time
            (8, "uint32", attr[8]),     # total_timer_time
            (9, "uint32", attr[9]),     # total_distance
            (11, "uint16", attr[10]),   # total_calories
            (13, "uint16", attr[11]),   # avg_speed
            (14, "uint16", attr[12]),   # max_speed
            (15, "uint8", attr[13]),    # avg_heart_rate
            (16, "uint8", attr[14]),    # max_heart_rate
            (17, "uint8", attr[15]),    # avg_cadence
            (18, "uint8", attr[16]),    # max_cadence
            (19, "uint16", attr[17]),   # avg_power
            (20, "uint16", attr[18]),   # max_power
            (254, "uint16", attr[0]),   # message_index
        ]

    def output_byte(self):
        return write_field(self.id, self.fields, self.write_data, self.record_id)


class record:
    def __init__(self, attr=None):
        if attr is None:
            attr = [966665266, 0, 0, 0, 0, 0, 0, 0]
        self.id = 20
        self.record_id = 0
        self.write_data = True
        self.fields = [
            (253, "uint32", attr[0]),   # timestamp
            (0, "sint32", attr[1]),     # position_lat
            (1, "sint32", attr[2]),     # position_long
            (3, "uint8", attr[3]),      # heart_rate
            (4, "uint8", attr[4]),      # cadence
            (5, "uint32", attr[5]),     # distance
            (6, "uint16", attr[6]),     # speed
            (7, "uint16", attr[7]),     # power
        ]

    def output_byte(self):
        return write_field(self.id, self.fields, self.write_data, self.record_id)


def write_field(id, spec, write_data=True, record_id=0):
    # FIT base type table (Table 4-6 in the FIT SDK spec):
    # name -> (base_type_field, size_bytes, struct_format)
    types = {
        "enum":    (0x00, 1, "B"),
        "sint8":   (0x01, 1, "b"),
        "uint8":   (0x02, 1, "B"),
        "sint16":  (0x83, 2, "h"),
        "uint16":  (0x84, 2, "H"),
        "sint32":  (0x85, 4, "l"),
        "uint32":  (0x86, 4, "L"),
        "string":  (0x07, -1, "s"),
        "float32": (0x88, 4, "f"),
        "float64": (0x89, 8, "d"),
        "uint8z":  (0x0a, 1, "B"),
        "uint16z": (0x8b, 2, "S"),
        "uint32z": (0x8c, 4, "L"),
        "byte":    (0x0d, -1, "s"),
    }
    # Definition message: header=0x40, reserved=0, architecture=little-endian, global_msg_id, field_count
    header = (record_id & 0x0f) | 0x40
    ret = struct.pack("=BBBHB", header, 0, 0, id, len(spec))
    data = struct.pack("=B", record_id) if write_data else b""
    for field_num, type_name, value in spec:
        size_flag, size, size_type = types[type_name]
        ret += struct.pack("=BBB", field_num, size, size_flag)
        if write_data:
            data += struct.pack("=" + size_type, value)
    return [ret, data]


def fit_main_header():
    return struct.pack("=BBHL4sH", 14, 0x20, 2140, 0, b'.FIT', 0x0000)


def checksum(f):
    f.seek(0)
    data = f.read()
    crc_table = [
        0x0, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
        0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
    ]
    crc = 0
    for byte in data:
        tmp = crc_table[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ crc_table[byte & 0xF]
        tmp = crc_table[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ crc_table[(byte >> 4) & 0xF]
    f.write(struct.pack("=H", crc))
    return crc


def check_file_size(f):
    f.seek(0, 2)
    size = f.tell()
    f.seek(4, 0)
    f.write(struct.pack("=L", size - 14))
    return f


def heart_rate_zone_creator(heart_rate_zone_array, output_file):
    zone_message = hr_zone()
    output_file.write(zone_message.output_byte()[0])
    for zone in heart_rate_zone_array:
        zone_data = hr_zone(zone)
        output_file.write(zone_data.output_byte()[1])


def record_creator(index, record_array, output_file):
    for rec_data in record_array[index]:
        rec = record(rec_data)
        parts = rec.output_byte()
        output_file.write(parts[0])
        output_file.write(parts[1])
    return output_file


def laps_creator(laps_array, record_array, output_file):
    lap_def = lap()
    for index, current_lap in enumerate(laps_array):
        record_creator(index, record_array, output_file)
        lap_data = lap(current_lap)
        output_file.write(lap_def.output_byte()[0])
        output_file.write(lap_data.output_byte()[1])
    return output_file


def export_file(f, filename):
    with open(filename, "wb") as out:
        out.write(f.getbuffer())
    print(f"Exported to {filename}")


def default_test():
    output = io.BytesIO()
    fileid = file_id()
    ev_start = event(event_start)
    userpro = user_profile()
    sportrow = sport()
    max_heart_rate_row = zones_target()
    ev_stop = event(event_stop)
    acti = activity()
    sess = session()

    output.write(fit_main_header())
    output.write(fileid.output_byte())
    output.write(ev_start.output_byte())
    output.write(userpro.output_byte())
    output.write(max_heart_rate_row.output_byte())
    output.write(sportrow.output_byte())
    heart_rate_zone_creator(heart_rate_zones, output)
    laps_creator(laps, records, output)
    output.write(ev_stop.output_byte())
    sess_bytes = sess.output_byte()
    output.write(sess_bytes[0] + sess_bytes[1])
    acti_bytes = acti.output_byte()
    output.write(acti_bytes[0] + acti_bytes[1])

    check_file_size(output)
    checksum(output)
    export_file(output, "result.fit")


if __name__ == '__main__':
    default_test()
