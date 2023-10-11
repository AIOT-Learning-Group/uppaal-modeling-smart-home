
import json
from typing import Dict, List, Tuple
from .common import AnimationSpecification, KeyFrame, RawTraceFrame
from .layout import smart_home_layout_for_demo
from loguru import logger


def trace_to_stamp(trace: str) -> List[Tuple[float, float]]:
    raw_trace = trace.replace("[0]: ", "").replace(") (", "),(")
    points: List[Tuple[float, float]] = []
    for trace_point in raw_trace.split("),("):
        dims = trace_point.replace("(", "").replace(")", "").split(",")
        assert len(dims) == 2, "bad trace point: " + trace_point
        points.append((float(dims[0]), float(dims[1])))
    return points


def build_anim_spec(traces: str, raw_rules: str) -> AnimationSpecification:
    rules = [line.strip() for line in raw_rules.splitlines() if (
        not line.strip().startswith("#")) and len(line.strip()) > 0]
    rules_text = {"rule" + str(i+1): line for i, line in enumerate(rules)}
    keyframes: List[KeyFrame] = []
    lines = traces.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("[0]: "):
            target = lines[i-1].replace(":", "")
            if target == "humanposition" or target == "position":
                keyframes.extend(parse_position(trace_to_stamp(line)))
            elif target.startswith("rule"):
                keyframes.extend(parse_rule(
                    target, trace_to_stamp(line), rules_text))
            elif target in attributes:
                keyframes.extend(parse_attribute(target, trace_to_stamp(line)))
            else:
                processed = False
                for device in device_prefix:
                    if target.startswith(device):
                        keyframes.extend(parse_device(
                            target, trace_to_stamp(line)))
                        processed = True
                if not processed:
                    logger.warning(f"unprocessable target: {target}")
    for frame in keyframes:
        if frame["timestamp"] > 0.0:
            frame["timestamp"] /= 5
    return {"keyFrames": keyframes}


global last_pos
layout = smart_home_layout_for_demo()

# location_to_id = {
#     "out": 0,
#     "doorway": 1,
#     # "kitchen": 2,
#     # "bathroom": 3,
#     "home": 2,
#     # "guest_room": 5,
# }

location_to_id = {
    "out": 0,
    "living_room": 1,
    "kitchen": 2,
    "bathroom": 3,
}

id_to_location = {v: k for k, v in location_to_id.items()}


in_place_time = 2
stay_time = 10


def parse_position(raw_frames: List[RawTraceFrame]) -> List[KeyFrame]:
    keyframes: List[KeyFrame] = []
    for i, (stamp, value) in enumerate(raw_frames):
        if i > 0 and value != raw_frames[i-1][1]:
            path = layout.shortest_path(
                id_to_location[int(raw_frames[i-1][1])],
                id_to_location[int(value)])
            logger.info("use path:" + "->".join(path))
            for j in range(i - 2, -1, -1):
                if raw_frames[j][1] != raw_frames[i-1][1]:
                    break
            total_duration = stamp - raw_frames[j][0]
            # assert total_duration > (
            #     in_place_time + stay_time), "unable to plan: time duration too short"
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


def parse_rule(name: str, raw_frames: List[RawTraceFrame], rules_text: Dict[str, str]) -> List[KeyFrame]:
    keyframes: List[KeyFrame] = []
    for i, (stamp, value) in enumerate(raw_frames):
        if (i > 0) and (raw_frames[i-1][1]) == 0 and (value == 1):
            keyframes.append(
                {"timestamp": stamp, "name": rules_text[name], "type": 2, "animation": ""})
    return keyframes


attributes = ["temperature", "humidity", "pm_2_5", "received_msgs", "rain"]


def parse_attribute(name: str, raw_frames: List[RawTraceFrame]) -> List[KeyFrame]:
    keyframes: List[KeyFrame] = []
    for stamp, value in raw_frames:
        keyframes.append(
            {"timestamp": stamp, "name": name, "type": 1, "animation": str(value)})
    return keyframes


device_prefix = ["door", "fan", "curtain",
                 "airconditioner", "sms", "window", "light"]


def parse_device(name: str, raw_frames: List[RawTraceFrame]) -> List[KeyFrame]:
    keyframes: List[KeyFrame] = []
    for stamp, value in raw_frames:
        if stamp > 0:
            keyframes.append(
                {"timestamp": stamp, "name": name, "type": 0, "animation": str(int(value))})
    return keyframes


if __name__ == "__main__":
    trace_input = "models/rq3_case_10.xml.result"
    tap_input = "taps/RQ3Case10.txt"
    open(trace_input + ".json", "w").write(json.dumps(build_anim_spec(
        open(trace_input, "r").read(), open(tap_input, "r").read()), indent=2))
