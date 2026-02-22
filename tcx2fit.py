import io
import argparse
from pathlib import Path

import TCXextractor
import FITpreparator
import ToFit


def main(file, age, weight, vo2max, gender):
    root, amount_laps = TCXextractor.load_tcx(file)
    total_strokes = TCXextractor.extract_total_strokes(root)
    lap_total_array, record_array = TCXextractor.extract_lap_records(root, amount_laps, age, weight, vo2max, gender)

    rounds = FITpreparator.record_preparator(record_array)
    laps = FITpreparator.lap_preparator(lap_total_array, record_array)
    events = FITpreparator.event_preparator(record_array)
    activity = FITpreparator.activity_preparator(record_array)
    session = FITpreparator.session_preparator(lap_total_array, record_array, total_strokes)

    output_path = Path(file).with_suffix('.fit')

    output = io.BytesIO()
    fileid = ToFit.file_id()
    ev_start = ToFit.event(events[0])
    userpro = ToFit.user_profile()
    sportrow = ToFit.sport()
    max_heart_rate_row = ToFit.zones_target()
    ev_stop = ToFit.event(events[1])
    acti = ToFit.activity(activity)
    sess = ToFit.session(session)

    output.write(ToFit.fit_main_header())
    output.write(fileid.output_byte())
    output.write(ev_start.output_byte())
    output.write(userpro.output_byte())
    output.write(max_heart_rate_row.output_byte())
    output.write(sportrow.output_byte())
    ToFit.laps_creator(laps, rounds, output)
    output.write(ev_stop.output_byte())
    sess_bytes = sess.output_byte()
    output.write(sess_bytes[0] + sess_bytes[1])
    acti_bytes = acti.output_byte()
    output.write(acti_bytes[0] + acti_bytes[1])

    ToFit.check_file_size(output)
    ToFit.checksum(output)
    ToFit.export_file(output, output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert a Coxswain TCX file to FIT format")
    parser.add_argument('-i', '--input', required=True, help="Path to the Coxswain TCX file")
    parser.add_argument('--age', type=int, default=33, help="Age of the user (default: 33)")
    parser.add_argument('--weight', type=int, default=78, help="Weight in kg (default: 78)")
    parser.add_argument('--vo2max', type=int, default=45, help="VO2max (default: 45)")
    parser.add_argument('--gender', type=str, choices=['m', 'f'], default='m', help="Gender: m or f (default: m)")
    args = parser.parse_args()
    main(args.input, args.age, args.weight, args.vo2max, args.gender)
