from lxml import etree
import numpy as np
from datetime import datetime
import FITpreparator
import os
import ToFit
import io
import sys

# namespaces
ns = {
    'ts': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
    'g': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
}
# date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
# epoch = (datetime.fromisoformat("1989-12-31 00:00:00"))
# test = datetime.strptime('2008-09-26T01:51:42.000Z', date_format)
# result_diff = int((test-epoch).total_seconds())


#test_sec = round((datetime.now() - epoch).total_seconds())
#print(test_sec)

class lapcreator:
    def __init__(self, tp, age=33, weight=78, vo2max=45, gender="m"):
        self.StartTime = 0
        self.TotalTimeSeconds = 0
        self.DistanceMeters = 0
        self.MaximumSpeed = 0
        self.Calories = 0
        self.AverageHeartRateBpm = 0
        self.MaximumHeartRateBpm = 0
        self.AvgSpeed = 0
        self.MaxBikeCadence = 0
        self.MeanBikeCadence = 0
        self.AvgWatts = 0
        self.MaxWatts = 0
        self.Intensity = 'Active'
        self.TriggerMethod = 'Manual'
        self.tp = tp
        self.trackpointkpi = []
        self.Totaltrackpointkpi = []
        self.index = 0
        self.Totaltrackpointkpi =[]
        self.kcalgenkomplet = []
        self.lapKPI = []
        self.age = age
        self.weight = weight
        self.vo2max = vo2max
        self.gender = gender
        # vo2max
        #self.stepsectot = []

    def lapcreatorfunc(self):
        if not self.tp: # If no trackpoints for this lap
            # Return default values to avoid errors downstream
            return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'Active', 'Manual'], []

        # this loop extract from the xml range the needed info for each track point
        for x in range(len(self.tp)):
            trackpoint_element = self.tp[x]

            time_text = trackpoint_element.xpath("ts:Time", namespaces=ns)[0].text if trackpoint_element.xpath("ts:Time", namespaces=ns) else None
            latitude = trackpoint_element.xpath("ts:Position/ts:LatitudeDegrees", namespaces=ns)[0].text if trackpoint_element.xpath("ts:Position/ts:LatitudeDegrees", namespaces=ns) else None
            longitude = trackpoint_element.xpath("ts:Position/ts:LongitudeDegrees", namespaces=ns)[0].text if trackpoint_element.xpath("ts:Position/ts:LongitudeDegrees", namespaces=ns) else None
            heart_rate = trackpoint_element.xpath("ts:HeartRateBpm/ts:Value", namespaces=ns)[0].text if trackpoint_element.xpath("ts:HeartRateBpm/ts:Value", namespaces=ns) else None
            cadence = trackpoint_element.xpath("ts:Cadence", namespaces=ns)[0].text if trackpoint_element.xpath("ts:Cadence", namespaces=ns) else None
            distance_meters = trackpoint_element.xpath("ts:DistanceMeters", namespaces=ns)[0].text if trackpoint_element.xpath("ts:DistanceMeters", namespaces=ns) else None
            speed = trackpoint_element.xpath("ts:Extensions/g:TPX/g:Speed", namespaces=ns)[0].text if trackpoint_element.xpath("ts:Extensions/g:TPX/g:Speed", namespaces=ns) else None
            watts = trackpoint_element.xpath("ts:Extensions/g:TPX/g:Watts", namespaces=ns)[0].text if trackpoint_element.xpath("ts:Extensions/g:TPX/g:Watts", namespaces=ns) else None

            trackpointkpi = [time_text, latitude, longitude, heart_rate, cadence, distance_meters, speed, watts]
            self.Totaltrackpointkpi.append(trackpointkpi)

        # Calc of the burned Calories of the body

        for x in range(len(self.tp)):
            heart_rate_value = float(heart_rate) if heart_rate is not None else 0.0

            if self.gender == "m":
                self.kcalgen = (-95.7735 + (0.634 * heart_rate_value) + (0.404 * self.vo2max) + (0.394 * self.weight) + (0.271 * self.age)) *(1/60) / 4.184
            elif self.gender == "f":
                self.kcalgen = (-59.3954 + (0.45 * heart_rate_value) + (0.380 * self.vo2max) + (0.103 * self.weight) + (0.274 * self.age)) *(1/60) / 4.184
            else: # Default to male if gender is unknown or invalid
                self.kcalgen = (-95.7735 + (0.634 * heart_rate_value) + (0.404 * self.vo2max) + (0.394 * self.weight) + (0.271 * self.age)) *(1/60) / 4.184
            self.kcalgenkomplet.append(self.kcalgen)

        self.Kcallap = np.sum(self.kcalgenkomplet,axis=0 )

        # KPI calculations

        self.TotaltrackpointkpiNP = np.atleast_2d(self.Totaltrackpointkpi)
        self.TotaltrackpointkpiNPnotime = np.array(self.TotaltrackpointkpiNP[:,3:])
        self.TotaltrackpointkpiNPnotime = self.TotaltrackpointkpiNPnotime.astype(float)
        self.meanarraykpi = np.mean(self.TotaltrackpointkpiNPnotime,axis=0)
        self.maxarraykpi = np.max(self.TotaltrackpointkpiNPnotime,axis=0)

        # creation of the time diff
        self.starttimecal = str(self.TotaltrackpointkpiNP[0,0])
        self.starttimecal = self.starttimecal[11:19]
        self.starttimecal = datetime.strptime(self.starttimecal, "%H:%M:%S")
        self.endtimecal = str(self.TotaltrackpointkpiNP[-1,0])
        self.endtimecal = self.endtimecal[11:19]
        self.endtimecal = datetime.strptime(self.endtimecal, "%H:%M:%S")

        # storing kpi into variables

        self.StartTime = self.TotaltrackpointkpiNP[0,0]
        self.TotalTimeSeconds = str((self.endtimecal - self.starttimecal).total_seconds())
        self.DistanceMeters = self.TotaltrackpointkpiNPnotime[-1,2] - self.TotaltrackpointkpiNPnotime[0,2]
        self.MaximumSpeed = self.maxarraykpi[3]
        self.Calories = self.Kcallap
        self.AverageHeartRateBpm = self.meanarraykpi[0]
        self.MaximumHeartRateBpm = self.maxarraykpi[0]
        self.AvgSpeed = self.meanarraykpi[3]
        self.MaxBikeCadence = self.maxarraykpi[1]
        self.MeanBikeCadence = self.meanarraykpi[1]
        self.AvgWatts = self.meanarraykpi[4]
        self.MaxWatts = self.maxarraykpi[4]
        self.Intensity = 'Active'
        self.TriggerMethod = 'Manual'

        self.lapKPI = [self.StartTime,
                       self.TotalTimeSeconds,   # total_timer_time
                       self.DistanceMeters,     # total_distance
                       self.Calories,           # total_calories
                       self.AvgSpeed,  # avg_speed
                       self.MaximumSpeed,       # max_speed
                       self.AverageHeartRateBpm,
                       self.MaximumHeartRateBpm,    #max_hear_rate
                       self.MeanBikeCadence,
                       self.MaxBikeCadence,     # max_cadence
                       self.AvgWatts,           # avg_power
                       self.MaxWatts,           # max_power
                       self.Intensity,
                       self.TriggerMethod,
        ]
        return (self.lapKPI, self.Totaltrackpointkpi)

def lap_amount(tcx):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(tcx, parser)
    root = tree.getroot()

    """This part calculates the amount of laps for this run based on 500m sections """

    TotalLapDistance = root.xpath("//ts:Lap", namespaces=ns)[0]
    TotalDistance = int(float(TotalLapDistance[1].text))

    if TotalDistance % 500 == 0:
        AmountLaps = TotalDistance // 500
    else:
        AmountLaps= (TotalDistance // 500) + 1

    return(root,AmountLaps)

def Lap_record_extractor(root,AmountLaps, age, weight, vo2max, gender):
    lap_total_array = []
    record_total_array = []
    for x in range(AmountLaps):

        #print(x)
        tp = root.xpath("//ts:Trackpoint[.//ts:DistanceMeters <"+ str(500*(x+1))+"][.//ts:DistanceMeters >="+ str(500*x)+"]", namespaces=ns)
        #print(tp[0][0].text)
        lap = lapcreator(tp, age, weight, vo2max, gender)
        lap_array, record_array = lap.lapcreatorfunc()
        lap_total_array.append(lap_array)
        record_total_array.append(record_array)
        #print(record_array)
        #print(len(tp))
    return(lap_total_array, record_total_array)

def total_stroke_extractor(root):
    total_strokes_elements = root.xpath("//g:Steps", namespaces=ns)
    if total_strokes_elements:
        total_strokes = int(total_strokes_elements[0].text)
    else:
        total_strokes = 0
    return total_strokes

def main(tcx_file_path, age, weight, vo2max, gender):

    rootxml, Amountlaps = lap_amount(tcx_file_path)
    total_strokes = total_stroke_extractor(rootxml)
    lap_total_array, record_array = Lap_record_extractor(rootxml,Amountlaps, age, weight, vo2max, gender)
    rounds = FITpreparator.record_preperator(record_array)
    laps = FITpreparator.lap_preperator(lap_total_array,record_array)
    print(laps)
    events = FITpreparator.event_preperator(record_array)
    activity = FITpreparator.activity_preparator(record_array)
    session = FITpreparator.session_preparator(lap_total_array, record_array, total_strokes)
    # Derive output filename
    base_name = os.path.basename(tcx_file_path)
    file_name_without_ext = os.path.splitext(base_name)[0]
    output_fit_file_path = os.path.join(os.path.dirname(tcx_file_path), file_name_without_ext + ".fit")

    output = io.BytesIO() # is the in memory file to store the bytes and interacte with them
    fileid = ToFit.file_id()
    ev_start = ToFit.event(events[0]) # Use events[0] for event_start
    userpro = ToFit.user_profile()
    sportrow = ToFit.sport()
    max_heart_rate_row = ToFit.zones_target()
    ev_stop = ToFit.event(events[1]) # Use events[1] for event_stop

    output.write(ToFit.fit_main_header())
    output.write(fileid.output_byte())
    output.write(ev_start.output_byte())
    output.write(userpro.output_byte())
    output.write(max_heart_rate_row.output_byte())
    output.write(sportrow.output_byte())
    ToFit.heart_rate_zone_creator(ToFit.hear_rate_zones, output) # Assuming default heart rate zones are acceptable or need to be derived
    ToFit.laps_creator(laps, rounds, output) # Use local 'laps' and 'rounds'
    output.write(ev_stop.output_byte())
    output.write(ToFit.session(session).output_byte()[0] + ToFit.session(session).output_byte()[1]) # Use local 'session'
    output.write(ToFit.activity(activity).output_byte()[0] + ToFit.activity(activity).output_byte()[1]) # Use local 'activity'

    ToFit.check_file_size(output)
    ToFit.checksum(output)
    ToFit.export_file(output, output_fit_file_path)

    print("done")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        tcx_file_path = sys.argv[1]
        main(tcx_file_path)
    else:
        print("Usage: python3 TCXextractor.py <path_to_tcx_file>")
