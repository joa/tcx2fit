"""
Tests that power data (avg_power, max_power, per-record watts) survives the
TCX → FIT conversion intact, for both the standard 500m-lap mode and the
workout/laps mode.

TSS (Training Stress Score) and IF (Intensity Factor) are computed by downstream
analytics apps from the power fields written into the FIT file.  If those fields
are zeroed out, TSS / IF will be reported as 0, losing all training load data.

The primary regression tested here:
  When the last workout step receives no trackpoints (activity ended before the
  planned workout finished), session_preparator / activity_preparator /
  event_preparator accessed records[-1][-1] on an empty list and silently
  returned all-zero session data, discarding every metric used for TSS and IF.
"""
import io
import os
import sys
import tempfile
from datetime import datetime, timedelta

import fitparse
import pytest

sys.path.insert(0, os.path.dirname(__file__))
import FITpreparator
import TCXextractor
import ToFit

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NS_TS = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
_NS_G = "http://www.garmin.com/xmlschemas/ActivityExtension/v2"


def make_tcx(n_trackpoints: int = 10, watts: int = 200, hr: int = 150,
             cad: int = 24, spd: float = 3.33) -> str:
    """Return a minimal but valid Coxswain-style TCX XML string.

    Each trackpoint is 1 minute and 200 m apart.  No GPS position is included
    (indoor rowing), so lat/lon remain None after parsing.
    """
    t0 = datetime(2024, 1, 1, 12, 0, 0)
    tps_xml = ""
    for i in range(n_trackpoints):
        t = t0 + timedelta(minutes=i)
        dist = i * 200.0
        tps_xml += f"""
          <Trackpoint>
            <Time>{t.strftime('%Y-%m-%dT%H:%M:%SZ')}</Time>
            <HeartRateBpm><Value>{hr}</Value></HeartRateBpm>
            <Cadence>{cad}</Cadence>
            <DistanceMeters>{dist}</DistanceMeters>
            <Extensions>
              <TPX xmlns="{_NS_G}">
                <Speed>{spd}</Speed>
                <Watts>{watts}</Watts>
              </TPX>
            </Extensions>
          </Trackpoint>"""

    total_dist = (n_trackpoints - 1) * 200
    total_time = (n_trackpoints - 1) * 60

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase xmlns="{_NS_TS}">
  <Activities>
    <Activity Sport="Biking">
      <Lap StartTime="{t0.strftime('%Y-%m-%dT%H:%M:%SZ')}">
        <TotalTimeSeconds>{total_time}</TotalTimeSeconds>
        <DistanceMeters>{total_dist}</DistanceMeters>
        <Track>{tps_xml}
        </Track>
      </Lap>
    </Activity>
  </Activities>
</TrainingCenterDatabase>"""


def run_conversion(lap_total_array, record_array, total_strokes: int = 0) -> bytes:
    """Run the full FIT preparation pipeline and return the raw FIT bytes."""
    rounds = FITpreparator.record_preparator(record_array)
    laps = FITpreparator.lap_preparator(lap_total_array, record_array)
    events = FITpreparator.event_preparator(record_array)
    activity = FITpreparator.activity_preparator(record_array)
    session = FITpreparator.session_preparator(
        lap_total_array, record_array, total_strokes
    )

    output = io.BytesIO()
    output.write(ToFit.fit_main_header())
    output.write(ToFit.file_id().output_byte())
    output.write(ToFit.event(events[0]).output_byte())
    output.write(ToFit.user_profile().output_byte())
    output.write(ToFit.zones_target().output_byte())
    output.write(ToFit.sport().output_byte())
    ToFit.laps_creator(laps, rounds, output)
    output.write(ToFit.event(events[1]).output_byte())
    sess_bytes = ToFit.session(session).output_byte()
    output.write(sess_bytes[0] + sess_bytes[1])
    acti_bytes = ToFit.activity(activity).output_byte()
    output.write(acti_bytes[0] + acti_bytes[1])

    ToFit.check_file_size(output)
    ToFit.checksum(output)
    return output.getvalue()


def parse_fit_power(data: bytes) -> dict:
    """Parse a FIT file and return dicts with power-related fields."""
    fit_file = fitparse.FitFile(io.BytesIO(data))
    result: dict = {"session": {}, "laps": [], "records": []}

    for msg in fit_file.get_messages("session"):
        result["session"] = {f.name: f.value for f in msg.fields}

    for msg in fit_file.get_messages("lap"):
        result["laps"].append({f.name: f.value for f in msg.fields})

    for msg in fit_file.get_messages("record"):
        result["records"].append({f.name: f.value for f in msg.fields})

    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_power_preserved_standard_mode():
    """Power data must survive the standard 500 m-per-lap conversion."""
    tcx_content = make_tcx(n_trackpoints=10, watts=200)

    with tempfile.NamedTemporaryFile(suffix=".tcx", mode="w", delete=False) as f:
        f.write(tcx_content)
        tcx_path = f.name

    try:
        root, amount_laps = TCXextractor.load_tcx(tcx_path)
        lap_total_array, record_array = TCXextractor.extract_lap_records(
            root, amount_laps, age=33, weight=78, vo2max=45, gender="m"
        )
        fit_data = run_conversion(lap_total_array, record_array)
        parsed = parse_fit_power(fit_data)

        session_avg_power = parsed["session"].get("avg_power")
        assert session_avg_power == 200, (
            f"Standard mode: session avg_power is {session_avg_power}, expected 200. "
            "Power data was lost during TCX→FIT conversion."
        )

        for rec in parsed["records"]:
            assert rec["power"] == 200, (
                f"Standard mode: record power is {rec['power']}, expected 200."
            )
    finally:
        os.unlink(tcx_path)


def test_power_preserved_laps_mode_all_groups_nonempty():
    """Power data must survive the workout/laps mode when all groups have data."""
    tcx_content = make_tcx(n_trackpoints=10, watts=200)

    with tempfile.NamedTemporaryFile(suffix=".tcx", mode="w", delete=False) as f:
        f.write(tcx_content)
        tcx_path = f.name

    try:
        root, _ = TCXextractor.load_tcx(tcx_path)
        all_tp = TCXextractor.extract_all_trackpoints(root)

        # Two non-empty groups simulate two workout steps
        groups = [all_tp[:5], all_tp[5:]]
        lap_total_array, record_array = TCXextractor.compute_lap_records(
            groups, age=33, weight=78, vo2max=45, gender="m"
        )
        fit_data = run_conversion(lap_total_array, record_array)
        parsed = parse_fit_power(fit_data)

        session_avg_power = parsed["session"].get("avg_power")
        assert session_avg_power == 200, (
            f"Laps mode (all non-empty): session avg_power is {session_avg_power}, "
            "expected 200."
        )

        active_laps = [
            lap for lap in parsed["laps"]
            if lap.get("total_elapsed_time", 0) > 0
        ]
        for lap in active_laps:
            assert lap.get("avg_power") == 200, (
                f"Laps mode: lap avg_power is {lap.get('avg_power')}, expected 200."
            )
    finally:
        os.unlink(tcx_path)


def test_power_preserved_laps_mode_empty_last_group():
    """Power data must survive when the last workout step has no trackpoints.

    This is the primary regression: the athlete stopped before completing the
    last planned workout step, leaving that step's trackpoint group empty.
    Before the fix, session_preparator detected records[-1] == [] and returned
    an all-zero session, wiping out avg_power, max_power, and total_work—
    the exact inputs needed by apps to compute TSS and IF.
    """
    tcx_content = make_tcx(n_trackpoints=10, watts=200)

    with tempfile.NamedTemporaryFile(suffix=".tcx", mode="w", delete=False) as f:
        f.write(tcx_content)
        tcx_path = f.name

    try:
        root, _ = TCXextractor.load_tcx(tcx_path)
        all_tp = TCXextractor.extract_all_trackpoints(root)

        # Three groups: two with data, one empty (activity ended before cooldown step)
        groups = [all_tp[:6], all_tp[6:], []]

        lap_total_array, record_array = TCXextractor.compute_lap_records(
            groups, age=33, weight=78, vo2max=45, gender="m"
        )
        fit_data = run_conversion(lap_total_array, record_array)
        parsed = parse_fit_power(fit_data)

        session_avg_power = parsed["session"].get("avg_power")
        assert session_avg_power == 200, (
            f"Laps mode (empty last group): session avg_power is {session_avg_power}, "
            "expected 200. The empty last workout step must not zero-out session data. "
            "TSS/IF inputs (avg_power, total_work) have been lost."
        )

        for rec in parsed["records"]:
            assert rec["power"] == 200, (
                f"Laps mode: record power is {rec['power']}, expected 200."
            )
    finally:
        os.unlink(tcx_path)


def test_power_preserved_laps_mode_empty_first_group():
    """Power data must survive when the first workout step has no trackpoints.

    An empty first group (e.g. the activity started mid-workout) triggered the
    same all-zero session bug via records[0] == [].
    """
    tcx_content = make_tcx(n_trackpoints=10, watts=200)

    with tempfile.NamedTemporaryFile(suffix=".tcx", mode="w", delete=False) as f:
        f.write(tcx_content)
        tcx_path = f.name

    try:
        root, _ = TCXextractor.load_tcx(tcx_path)
        all_tp = TCXextractor.extract_all_trackpoints(root)

        # Empty warmup step followed by two real steps
        groups = [[], all_tp[:6], all_tp[6:]]

        lap_total_array, record_array = TCXextractor.compute_lap_records(
            groups, age=33, weight=78, vo2max=45, gender="m"
        )
        fit_data = run_conversion(lap_total_array, record_array)
        parsed = parse_fit_power(fit_data)

        session_avg_power = parsed["session"].get("avg_power")
        assert session_avg_power == 200, (
            f"Laps mode (empty first group): session avg_power is {session_avg_power}, "
            "expected 200. An empty warmup step must not zero-out session data."
        )
    finally:
        os.unlink(tcx_path)
