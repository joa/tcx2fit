from lxml import etree
import numpy as np
from datetime import datetime

ns = {
    'ts': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
    'g': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
}


class LapCreator:
    def __init__(self, tp, age=33, weight=78, vo2max=45, gender="m"):
        self.tp = tp
        self.age = age
        self.weight = weight
        self.vo2max = vo2max
        self.gender = gender
        self.kcal_values = []
        self.trackpoints = []

    def build(self):
        if not self.tp:
            return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'Active', 'Manual'], []

        heart_rate = None
        for trackpoint_element in self.tp:
            def _get(xpath):
                nodes = trackpoint_element.xpath(xpath, namespaces=ns)
                return nodes[0].text if nodes else None

            time_text = _get("ts:Time")
            latitude = _get("ts:Position/ts:LatitudeDegrees")
            longitude = _get("ts:Position/ts:LongitudeDegrees")
            heart_rate = _get("ts:HeartRateBpm/ts:Value")
            cadence = _get("ts:Cadence")
            distance_meters = _get("ts:DistanceMeters")
            speed = _get("ts:Extensions/g:TPX/g:Speed")
            watts = _get("ts:Extensions/g:TPX/g:Watts")
            self.trackpoints.append([time_text, latitude, longitude, heart_rate, cadence, distance_meters, speed, watts])

        # Calorie calculation uses the heart rate from the last trackpoint for all intervals
        heart_rate_value = float(heart_rate) if heart_rate is not None else 0.0
        for _ in self.tp:
            if self.gender == "f":
                kcal = (-59.3954 + (0.45 * heart_rate_value) + (0.380 * self.vo2max) + (0.103 * self.weight) + (0.274 * self.age)) * (1 / 60) / 4.184
            else:
                kcal = (-95.7735 + (0.634 * heart_rate_value) + (0.404 * self.vo2max) + (0.394 * self.weight) + (0.271 * self.age)) * (1 / 60) / 4.184
            self.kcal_values.append(kcal)

        kcal_lap = np.sum(self.kcal_values, axis=0)

        data = np.atleast_2d(self.trackpoints)
        numeric = np.array(data[:, 3:]).astype(float)
        mean_kpi = np.mean(numeric, axis=0)
        max_kpi = np.max(numeric, axis=0)

        start_time = datetime.strptime(str(data[0, 0])[11:19], "%H:%M:%S")
        end_time = datetime.strptime(str(data[-1, 0])[11:19], "%H:%M:%S")

        lap_kpi = [
            data[0, 0],                              # StartTime
            str((end_time - start_time).total_seconds()),  # TotalTimeSeconds
            numeric[-1, 2] - numeric[0, 2],          # DistanceMeters
            kcal_lap,                                 # Calories
            mean_kpi[3],                              # AvgSpeed
            max_kpi[3],                               # MaximumSpeed
            mean_kpi[0],                              # AverageHeartRateBpm
            max_kpi[0],                               # MaximumHeartRateBpm
            mean_kpi[1],                              # MeanBikeCadence
            max_kpi[1],                               # MaxBikeCadence
            mean_kpi[4],                              # AvgWatts
            max_kpi[4],                               # MaxWatts
            'Active',
            'Manual',
        ]
        return lap_kpi, self.trackpoints


def load_tcx(tcx):
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.parse(tcx, parser).getroot()

    # Lap count is derived from 500 m sections
    first_lap = root.xpath("//ts:Lap", namespaces=ns)[0]
    total_distance = int(float(first_lap[1].text))
    amount_laps = total_distance // 500 if total_distance % 500 == 0 else (total_distance // 500) + 1

    return root, amount_laps


def extract_lap_records(root, amount_laps, age, weight, vo2max, gender):
    lap_total_array = []
    record_total_array = []
    for i in range(amount_laps):
        tp = root.xpath(
            f"//ts:Trackpoint[.//ts:DistanceMeters <{500 * (i + 1)}][.//ts:DistanceMeters >={500 * i}]",
            namespaces=ns,
        )
        lap = LapCreator(tp, age, weight, vo2max, gender)
        lap_array, record_array = lap.build()
        lap_total_array.append(lap_array)
        record_total_array.append(record_array)
    return lap_total_array, record_total_array


def extract_total_strokes(root):
    elements = root.xpath("//g:Steps", namespaces=ns)
    return int(elements[0].text) if elements else 0
