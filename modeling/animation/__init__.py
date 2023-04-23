
from typing_extensions import TypedDict
import json
from typing import List, Tuple
from .layout import smart_home_layout
from loguru import logger

RawFrame = Tuple[float, float]
KeyFrame = TypedDict(
    'KeyFrame', {'type': int, 'name': str, "animation": str, "timestamp": float})
AnimationSpecification = TypedDict('AnimationSpecification', {
                                   'keyFrames': List[KeyFrame]})


def trace_to_stamp(trace: str) -> List[Tuple[float, float]]:
    raw_trace = trace.replace("[0]: ", "").replace(") (", "),(")
    points: List[Tuple[float, float]] = []
    for trace_point in raw_trace.split("),("):
        dims = trace_point.replace("(", "").replace(")", "").split(",")
        assert len(dims) == 2, "bad trace point: " + trace_point
        points.append((float(dims[0]), float(dims[1])))
    return points


def build_anim_spec(traces: str) -> AnimationSpecification:
    keyframes: List[KeyFrame] = []
    lines = traces.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("[0]: "):
            target = lines[i-1].replace(":", "")
            if target == "position":
                keyframes.extend(parse_position(trace_to_stamp(line)))
            elif target.startswith("rule"):
                keyframes.extend(parse_rule(target, trace_to_stamp(line)))
            elif target in attributes:
                keyframes.extend(parse_attribute(target, trace_to_stamp(line)))
            else:
                for device in device_prefix:
                    if target.startswith(device):
                        keyframes.extend(parse_device(
                            target, trace_to_stamp(line)))
    return {"keyFrames": keyframes}


global last_pos
layout = smart_home_layout()

location_to_id = {
    "out": 0,
    "living_room": 1,
    "kitchen": 2,
    "bathroom": 3,
    "bedroom": 4,
    "guest_room": 5,
}

id_to_location = {v: k for k, v in location_to_id.items()}


in_place_time = 2
stay_time = 10


def parse_position(raw_frames: List[RawFrame]) -> List[KeyFrame]:
    keyframes: List[KeyFrame] = []
    for i, (stamp, value) in enumerate(raw_frames):
        if i > 0 and value != raw_frames[i-1][1]:
            path = layout.shortest_path(
                id_to_location[int(raw_frames[i-1][1])],
                id_to_location[int(value)])
            for j in range(i - 2, -1, -1):
                if raw_frames[j][1] != raw_frames[i-1][1]:
                    break
            total_duration = stamp - raw_frames[j][0]
            assert total_duration > (
                in_place_time + stay_time), "unable to plan: time duration too short"
            logger.info("total_duration: " + str(total_duration))
            keyframes.append(
                {"timestamp": raw_frames[j][0] + stay_time, "name": path[0], "type": 3, "animation": ""})

            duration_for_move = total_duration - in_place_time - stay_time
            for i, node in enumerate(path):
                if i > 0:
                    keyframes.append(
                        {"timestamp": raw_frames[j][0] + stay_time + duration_for_move / (len(path) - 1) * i, "name": node, "type": 3, "animation": ""})

            # print([(kf["timestamp"], kf["name"]) for kf in keyframes])
        else:
            pass

    return keyframes


rule_text = {
    "rule1": "IF Human.out THEN door_0.open_door",
    "rule2": "IF Human.living_room THEN curtain_0.open_curtain",
    "rule3": "IF temperature>19.6 THEN fan_0.turn_fan_on"
}


def parse_rule(name: str, raw_frames: List[RawFrame]) -> List[KeyFrame]:
    keyframes: List[KeyFrame] = []
    for i, (stamp, value) in enumerate(raw_frames):
        if (i > 0) and (raw_frames[i-1][1]) == 0 and (value == 1):
            keyframes.append(
                {"timestamp": stamp, "name": rule_text[name], "type": 2, "animation": ""})
    return keyframes


attributes = ["temperature"]


def parse_attribute(name: str, raw_frames: List[RawFrame]) -> List[KeyFrame]:
    keyframes: List[KeyFrame] = []
    for stamp, value in raw_frames:
        keyframes.append(
            {"timestamp": stamp, "name": name, "type": 1, "animation": str(value)})
        # print(name, value, "when", stamp)
    return keyframes


device_prefix = ["door", "fan", "curtain"]


def parse_device(name: str, raw_frames: List[RawFrame]) -> List[KeyFrame]:
    keyframes: List[KeyFrame] = []
    for stamp, value in raw_frames:
        if stamp > 0:
            keyframes.append(
                {"timestamp": stamp, "name": name, "type": 0, "animation": str(value)})
    return keyframes


if __name__ == "__main__":
    open("specifications/case_study.json", "w").write(json.dumps(
        build_anim_spec(open("models/rq3_case_study.xml.result", "r").read())))
