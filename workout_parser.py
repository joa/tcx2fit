from datetime import datetime

import fitparse


def load_workout(path):
    """Load and expand workout steps from a FIT file.

    Returns a flat list of dicts: {name, duration (float | None), intensity}.
    Repeat blocks are expanded into individual step occurrences.
    """
    fit = fitparse.FitFile(path)
    raw_steps = []
    for msg in fit.get_messages('workout_step'):
        d = {f.name: f.value for f in msg.fields}
        duration_type = d.get('duration_type')
        if duration_type == 'repeat_until_steps_cmplt':
            raw_steps.append({
                'duration_type': 'repeat_until_steps_cmplt',
                'duration_step': d.get('duration_step'),
                'repeat_steps': d.get('repeat_steps'),
                'message_index': d.get('message_index'),
            })
        else:
            raw_steps.append({
                'name': d.get('wkt_step_name'),
                'duration': d.get('duration_time'),  # seconds or None for open steps
                'intensity': d.get('intensity'),
                'duration_type': duration_type,
                'message_index': d.get('message_index'),
            })
    return _expand_steps(raw_steps)


def _expand_steps(raw_steps):
    """Expand repeat blocks into a flat list of steps.

    Each repeat_until_steps_cmplt marker references the message_index to go
    back to (duration_step) and the number of *additional* iterations
    (repeat_steps) beyond the one already executed.
    """
    result = []
    for i, step in enumerate(raw_steps):
        if step['duration_type'] == 'repeat_until_steps_cmplt':
            target_msg_idx = step['duration_step']
            # Locate the start of the repeating block in the raw list
            start_i = next(
                j for j, s in enumerate(raw_steps)
                if s.get('message_index') == target_msg_idx
            )
            # Collect non-repeat steps that form the block
            block = [
                s for s in raw_steps[start_i:i]
                if s['duration_type'] != 'repeat_until_steps_cmplt'
            ]
            for _ in range(step['repeat_steps']):
                result.extend(block)
        else:
            result.append(step)
    return result


def split_trackpoints_by_steps(trackpoints, steps):
    """Assign trackpoints to workout steps by elapsed time.

    trackpoints: list of [time_str, lat, lon, hr, cad, dist, spd, watt]
                 where time_str is formatted '%Y-%m-%dT%H:%M:%SZ'
    steps:       expanded list of step dicts from load_workout()

    Returns a list (one entry per step) of trackpoint sub-lists.
    Empty sub-lists are produced for steps that received no trackpoints
    (e.g. the athlete stopped early).
    """
    if not trackpoints:
        return [[] for _ in steps]

    fmt = '%Y-%m-%dT%H:%M:%SZ'
    t_start = datetime.strptime(trackpoints[0][0], fmt)
    t_end = datetime.strptime(trackpoints[-1][0], fmt)
    total_seconds = (t_end - t_start).total_seconds()

    timed_total = sum(s['duration'] for s in steps if s['duration'] is not None)
    open_count = sum(1 for s in steps if s['duration'] is None)
    open_duration = (
        (total_seconds - timed_total) / open_count if open_count > 0 else 0.0
    )

    # Build cumulative (start_sec, end_sec) boundaries for each step
    boundaries = []
    cursor = 0.0
    for step in steps:
        d = step['duration'] if step['duration'] is not None else open_duration
        boundaries.append((cursor, cursor + d))
        cursor += d

    groups = [[] for _ in steps]
    last = len(steps) - 1
    for tp in trackpoints:
        elapsed = (datetime.strptime(tp[0], fmt) - t_start).total_seconds()
        placed = False
        for idx, (start, end) in enumerate(boundaries):
            if start <= elapsed < end:
                groups[idx].append(tp)
                placed = True
                break
        if not placed:
            groups[last].append(tp)

    return groups
