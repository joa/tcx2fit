import ToFit
import TCXextractor
import FITpreparator
import io
import datetime
import argparse
import os



def main(file, age, weight, vo2max, gender):

    rootxml, Amountlaps = TCXextractor.lap_amount(file)
    total_strokes = TCXextractor.total_stroke_extractor(rootxml)
    lap_total_array, record_array = TCXextractor.Lap_record_extractor(rootxml, Amountlaps, age, weight, vo2max, gender)
    rounds = FITpreparator.record_preperator(record_array)
    laps = FITpreparator.lap_preperator(lap_total_array,record_array)
    events = FITpreparator.event_preperator(record_array)
    activity = FITpreparator.activity_preparator(record_array)
    session = FITpreparator.session_preparator(lap_total_array, record_array, total_strokes)

    # Derive output filename
    base_name = os.path.basename(file)
    file_name_without_ext = os.path.splitext(base_name)[0]
    output_fit_file_path = os.path.join(os.path.dirname(file), file_name_without_ext + ".fit")

    output = io.BytesIO() # is the in memory file to store the bytes and interacte with them
    fileid = ToFit.file_id()
    ev_start = ToFit.event(events[0])
    userpro = ToFit.user_profile()
    sportrow = ToFit.sport()
    max_heart_rate_row = ToFit.zones_target()
    ev_stop = ToFit.event(events[1])
    acti = ToFit.activity(activity)
    sess = ToFit.session(session)
    output.write(ToFit.fit_main_header())     # write header without the crc value and size of the file
    output.write(fileid.output_byte())  # write to output the file type here activity message def + data manufacturer
    print(">>> file_id message + data created")
    output.write(ev_start.output_byte())
    output.write(userpro.output_byte())
    output.write(max_heart_rate_row.output_byte())
    output.write(sportrow.output_byte())

    #heart_rate_zone_creator(hear_rate_zones, output)

    ToFit.laps_creator(laps,rounds, output)
    output.write(ev_stop.output_byte())
    output.write(sess.output_byte()[0] + sess.output_byte()[1]) # write to outputfile the sessions message + data
    print(">>> write data for session")
    output.write(acti.output_byte()[0] + acti.output_byte()[1]) # write to outputfile the activity message + data
    print(">>> write data for activity")
    ToFit.check_file_size(output)

############# perform crc check with the header and data and add the 2 bytes at the end of the file ####################

    ToFit.checksum(output)

############# create export data in fit format and export it into it. ##################################################

    ToFit.export_file(output, output_fit_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="takes the Coxswain TCX file and export it as FIT file")
    parser.add_argument('-i', '--input', help="give file path to the Coxswain TCX file")
    parser.add_argument('--age', type=int, default=33, help="Age of the user for calorie calculation (default: 33)")
    parser.add_argument('--weight', type=int, default=78, help="Weight of the user in kg for calorie calculation (default: 78)")
    parser.add_argument('--vo2max', type=int, default=45, help="VO2max of the user for calorie calculation (default: 45)")
    parser.add_argument('--gender', type=str, choices=['m', 'f'], default='m', help="Gender of the user (m for male, f for female) for calorie calculation (default: m)")
    args = parser.parse_args()
    main(args.input, args.age, args.weight, args.vo2max, args.gender)

