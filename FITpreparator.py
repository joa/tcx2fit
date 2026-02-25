from datetime import datetime
import numpy as np


def degree_to_semicircle(degree):
    return int(float(degree) * (2**31 / 180))


def epoch_calc_sec(training_datetime):
    epoch = datetime.fromisoformat("1989-12-31 00:00:00")
    dt = datetime.strptime(training_datetime, "%Y-%m-%dT%H:%M:%SZ")
    return int((dt - epoch).total_seconds())


def activity_preparator(record_array_tcx):
    records = record_preparator(record_array_tcx)
    flat_records = [r for lap in records for r in lap]

    if not flat_records:
        return [0, 0, 0]

    timestamp = flat_records[-1][0] + 1
    total_timer_time = (flat_records[-1][0] - flat_records[0][0]) * 100
    return [timestamp, total_timer_time, 1]


def session_preparator(lap_total_array_tcx, record_array_tcx, total_strokes_tcx):
    session_records = record_preparator(record_array_tcx)
    session_lap = lap_preparator(lap_total_array_tcx, record_array_tcx)

    flat_records = [record for lap in session_records for record in lap]

    if not flat_records:
        return [0] * 22

    session_mean = list(map(int, np.mean(flat_records, axis=0)))
    session_max = np.max(flat_records, axis=0)
    session_totals = np.sum(session_lap, axis=0) if session_lap else [0] * 19

    timestamp = flat_records[-1][0] + 1
    start_time = flat_records[0][0]
    start_position_lat = flat_records[0][1]
    start_position_long = flat_records[0][2]
    total_elapsed_time = (flat_records[-1][0] - flat_records[0][0]) * 1000
    total_distance = flat_records[-1][5] - flat_records[0][5]

    session = [
        timestamp,
        start_time,
        start_position_lat,
        start_position_long,
        4,                          # sport: Fitness Equipment
        14,                         # sub_sport: Indoor Rowing
        total_elapsed_time,
        total_elapsed_time,         # total_timer_time == total_elapsed_time
        total_distance,
        session_totals[10],         # total_calories (sum across laps)
        session_mean[6],            # avg_speed
        session_max[6],             # max_speed
        session_mean[3],            # avg_heart_rate
        session_max[3],             # max_heart_rate
        session_mean[4],            # avg_cadence
        session_max[4],             # max_cadence
        session_mean[7],            # avg_power
        session_max[7],             # max_power
        len(session_lap),           # num_lap
        session_mean[7] * (flat_records[-1][0] - flat_records[0][0]),  # total_work
        60,                         # min_heart_rate
        total_strokes_tcx,
    ]
    return list(map(int, session))


def lap_preparator(lap_total_array_tcx, record_array_tcx):
    lap_records = record_preparator(record_array_tcx)
    lap_total_array_fit = []

    for index, laps in enumerate(lap_total_array_tcx):
        if not lap_records[index]:
            lap_total_array_fit.append([0] * 19)
            continue

        timestamp = lap_records[index][-1][0]
        start_time = lap_records[index][0][0] if index == 0 else lap_records[index][0][0] + 1

        lap = [
            index,                                          # message_index
            timestamp,
            start_time,
            lap_records[index][0][1],                       # start_position_lat
            lap_records[index][0][2],                       # start_position_long
            lap_records[index][-1][1],                      # end_position_lat
            lap_records[index][-1][2],                      # end_position_long
            (lap_records[index][-1][0] - lap_records[index][0][0]) * 1000,  # total_elapsed_time
            (lap_records[index][-1][0] - lap_records[index][0][0]) * 1000,  # total_timer_time
            lap_total_array_tcx[index][2] * 100,            # total_distance
            lap_total_array_tcx[index][3],                  # total_calories
            lap_total_array_tcx[index][4] * 1000,           # avg_speed
            lap_total_array_tcx[index][5] * 1000,           # max_speed
            lap_total_array_tcx[index][6],                  # avg_heart_rate
            lap_total_array_tcx[index][7],                  # max_heart_rate
            lap_total_array_tcx[index][8],                  # avg_cadence
            lap_total_array_tcx[index][9],                  # max_cadence
            lap_total_array_tcx[index][10],                 # avg_power
            lap_total_array_tcx[index][11],                 # max_power
        ]
        lap_total_array_fit.append(list(map(int, lap)))

    return lap_total_array_fit


def record_preparator(record_array_tcx):
    records_array_fit = []

    for records in record_array_tcx:
        record_array_lap_fit = []
        for record in records:
            record_fit = [
                int(epoch_calc_sec(record[0])),
                int(degree_to_semicircle(record[1] if record[1] is not None else 0)),
                int(degree_to_semicircle(record[2] if record[2] is not None else 0)),
                int(float(record[3]) if record[3] is not None else 0),
                int(float(record[4]) if record[4] is not None else 0),
                int(float(record[5]) if record[5] is not None else 0) * 100,
                int(float(record[6]) * 1000),
                int(float(record[7]) if record[7] is not None else 0),
            ]
            record_array_lap_fit.append(record_fit)
        records_array_fit.append(record_array_lap_fit)

    return records_array_fit


def event_preparator(record_array_tcx):
    records = record_preparator(record_array_tcx)
    flat_records = [r for lap in records for r in lap]

    if not flat_records:
        return ([0, 0, 0, 1], [0, 0, 4, 0])

    event_start = [flat_records[0][0], 0, 0, 1]
    event_stop = [flat_records[-1][0], 0, 4, 0]
    return event_start, event_stop
