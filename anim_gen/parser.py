
import json
from anim_gen.layout import smart_home_layout


class KeyFrame:
    def __init__(self):
        self.type = ""
        self.name = ""
        self.animation = ""
        self.timestamp = ""


def trace_to_stamp(trace: str):
    return eval("[" + trace.replace("[0]: ", "").replace(") (", "),(") + "]")


def build_anim_spec(path: str):
    keyframes = []
    lines = open(path, "r").read().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("[0]: "):
            target = lines[i-1].replace(":", "")
            if target == "position":
                keyframes += parse_position(trace_to_stamp(line))
            elif target.startswith("rule"):
                keyframes += parse_rule(target, trace_to_stamp(line))
            elif target in attributes:
                keyframes += parse_attribute(target, trace_to_stamp(line))
            else:
                for device in device_prefix:
                    if target.startswith(device):
                        keyframes += parse_device(target, trace_to_stamp(line))
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


def parse_position(raw_frames: list):
    keyframes = []
    for i, (stamp, value) in enumerate(raw_frames):
        if i > 0 and value != raw_frames[i-1][1]:
            path = layout.shortest_path(
                id_to_location[raw_frames[i-1][1]], id_to_location[value])
            for j in range(i - 2, -1, -1):
                if raw_frames[j][1] != raw_frames[i-1][1]:
                    break
            total_duration = stamp - raw_frames[j][0]
            assert total_duration > (
                in_place_time + stay_time), "unable to plan: time duration too short"
            print(total_duration)
            keyframes.append(
                {"timestamp": raw_frames[j][0] + stay_time, "name": path[0], "type": 3, "animation": ""})

            duration_for_move = total_duration - in_place_time - stay_time
            for i, node in enumerate(path):
                if i > 0:
                    keyframes.append(
                        {"timestamp": raw_frames[j][0] + stay_time + duration_for_move / (len(path) - 1) * i, "name": node, "type": 3, "animation": ""})

            print([(kf["timestamp"], kf["name"]) for kf in keyframes])
        else:
            pass

    return keyframes


rule_text = {
    "rule1": "IF Human.out THEN door_0.open_door",
    "rule2": "IF Human.living_room THEN curtain_0.open_curtain",
    "rule3": "IF temperature>19.6 THEN fan_0.turn_fan_on"
}


def parse_rule(name: str, raw_frames: list):
    keyframes = []
    for i, (stamp, value) in enumerate(raw_frames):
        if (i > 0) and (raw_frames[i-1][1]) == 0 and (value == 1):
            keyframes.append(
                {"timestamp": stamp, "name": rule_text[name], "type": 2, "animation": ""})
            # print(name, "triggered on", stamp)
    return keyframes


attributes = ["temperature"]


def parse_attribute(name: str, raw_frames: list):
    keyframes = []
    for stamp, value in raw_frames:
        keyframes.append(
            {"timestamp": stamp, "name": name, "type": 1, "animation": str(value)})
        # print(name, value, "when", stamp)
    return keyframes


device_prefix = ["door", "fan", "curtain"]


def parse_device(name: str, raw_frames: list):
    keyframes = []
    for stamp, value in raw_frames:
        if stamp > 0:
            keyframes.append(
                {"timestamp": stamp, "name": name, "type": 0, "animation": str(value)})
    return keyframes


if __name__ == "__main__":
    open("specifications/case_study.json", "w").write(json.dumps(
        build_anim_spec("models/rq3_case_study.xml.result")))
