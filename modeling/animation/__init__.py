
import json
from typing import Dict, List, Tuple
from .common import AnimationSpecification, KeyFrame, RawTraceFrame
from .layout import smart_home_layout_for_demo
from modeling.utils import translated
from loguru import logger


def trace_to_stamp(trace: str) -> List[Tuple[float, float]]:
    raw_trace = trace.replace("[0]: ", "").replace(") (", "),(")
    points: List[Tuple[float, float]] = []
    for trace_point in raw_trace.split("),("):
        dims = trace_point.replace("(", "").replace(")", "").split(",")
        assert len(dims) == 2, "bad trace point: " + trace_point
        points.append((float(dims[0]), float(dims[1])))
    return points

attributes = ["temperature", "humidity", "pm25", "brightness", "co", "airquality"]


def build_anim_spec(traces: str, raw_rules: str) -> AnimationSpecification:
    rules = [line.strip() for line in raw_rules.splitlines() if (
        not line.strip().startswith("#")) and len(line.strip()) > 0]
    rules_text = {"rule" + str(i+1): line for i, line in enumerate(rules)}
    keyframes: List[KeyFrame] = []
    lines = traces.splitlines()
    all_rules = []
    rule_traces = {}
    positions = []
    for i, line in enumerate(lines):
        if line.startswith("[0]: "):
            target = lines[i-1].replace(":", "")
            if target == "humanposition" or target == "position":
                positions = trace_to_stamp(line)
                keyframes.extend(parse_position(positions))
            elif target.startswith("rule"):
                all_rules.append(target)
                rule_traces[target] = line
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
    keyframes += parse_all_rules(all_rules, rule_traces, rules_text)
    last_time = max([frame["timestamp"] for frame in keyframes])
    for stamp in range(round(last_time + 1)):
        keyframes.append(
            {"timestamp": stamp, "name": "time", "type": 1, "animation": str(stamp)})
    keyframes = add_device_hint(keyframes, positions)
    for frame in keyframes:
        # logger.info(f"{frame['timestamp']}, in {get_location(frame['timestamp'], positions)}")
        if frame["timestamp"] > 0.0:
            frame["timestamp"] /= 5
    
    return {"keyFrames": keyframes}

layout = smart_home_layout_for_demo()

device_in_layout = {
    "out": ['door[0]'],
    "living_room": ['light[0]', 'curtain[0]', 'fan[0]', 'airconditioner[0]', 'airpurifier[0]', 'humidifier[0]', 'dehumidifier[0]'],
    "bedroom": ['window[0]', 'light[1]', 'curtain[1]', 'door[1]', 'robotvacuum[0]'],
    "kitchen": ["coffeemachine[0]", "light[2]"],
    "kitchen": ["heater[0]", "light[3]"],
}

def get_layout(device_name:str):
    for k, v in device_in_layout.items():
        if device_name in v:
            return k
    return ""

def add_device_hint(keyframes: List[KeyFrame], positions):
    device_frames = [f for f in keyframes if f["type"] == 0]
    hint_frames = []
    for df in device_frames:
        user_loc = get_location(df["timestamp"], positions)
        dev_loc = get_layout(df["name"])
        if df['timestamp'] > 0 and user_loc != dev_loc:
            action_text = "触发"
            if df["name"] == 'airconditioner[0]':
                action_text = {0: '关闭', 1: '制冷', 2: '制热'}[int(df["animation"])]
            else:
                action_text = {0:'关闭', 1:'开启'}[int(df["animation"])]
            hint_frames.append({"timestamp": df["timestamp"], "name": translated(df["name"]) + "被设为" + action_text, "type": -1, "animation": ""})
    return keyframes + hint_frames

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
    "bedroom": 2,
    'kitchen': 3, 
    "bathroom": 4,
}

id_to_location = {v: k for k, v in location_to_id.items()}

duration_for_move = 10

def get_location(timestamp: float, raw_frames: List[RawTraceFrame]):
    for i, (stamp, value) in enumerate(raw_frames):
        if  stamp < timestamp:
            continue
        return id_to_location[value]

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

            # 上一个迁移过来，这一个的duration前10s给迁移的动画
            # assert total_duration > (
            #     in_place_time + stay_time), "unable to plan: time duration too short"

            keyframes.append(
                {"timestamp": raw_frames[i-1][0] - duration_for_move, "name": path[0], "type": 3, "animation": ""})
            
            logger.info("add*: " + str(raw_frames[i-1][0] - duration_for_move) + ", " + path[0])
            
            logger.info("total_duration: " + str(total_duration) + ", duration_for_move:" + str(duration_for_move))
            for k, node in enumerate(path):
                if k > 0:
                    logger.info("add: " + str(raw_frames[i-1][0] - duration_for_move + duration_for_move / (len(path) - 1) * k) + ", " + node)
                    keyframes.append({"timestamp": raw_frames[i-1][0] - duration_for_move + duration_for_move / (len(path) - 1) * k,
                                      "name": node, "type": 3, "animation": ""})
        else:
            pass
    return keyframes

def is_triggered(timestamp: float, raw_frames: List[RawTraceFrame]):
    i = 0
    stamp = raw_frames[i][0]
    while stamp <= timestamp:
        i += 1
        if i < len(raw_frames):
            stamp = raw_frames[i][0]
        else:
            return raw_frames[i-1][1] == 1
    if i > 0:
        return raw_frames[i-1][1] == 1
    else:
        return raw_frames[i][1] == 1

def parse_all_rules(all_rules: list[str], rule_traces: dict[str,str], rules_text: dict[str, str]):
    timestamps = []
    results: List[KeyFrame] = []
    rule_frames: dict[str, List[RawTraceFrame]] = {}
    for rule_name in all_rules:
        rule_frames[rule_name] = trace_to_stamp(rule_traces[rule_name])
        timestamps += [stamp for stamp, _ in rule_frames[rule_name]]
    timestamps = list(set(timestamps))
    
    for timestamp in timestamps:
        current_triggered = {rule_name: is_triggered(timestamp, rule_frames[rule_name]) for rule_name in all_rules}
        text_result = "\n".join(
            [f"<color={'green' if current_triggered[r] else 'grey'}>{rules_text[r]}</color>" for r in all_rules]
        )
        results.append(
            {"timestamp": timestamp, "name": translated(text_result), "type": 2, "animation": ""}
        )
    return results


# def parse_rule(name: str, raw_frames: List[RawTraceFrame], rules_text: Dict[str, str]) -> List[KeyFrame]:
#     keyframes: List[KeyFrame] = []
#     begin = -1
#     for i, (stamp, value) in enumerate(raw_frames): # 规则状态为 1 的区间内，每个单位时间都要触发规则
#         if value == 1 and raw_frames[i-1][1] == 0:
#             begin = stamp
#             continue
#         if begin != -1 and value == 0 and raw_frames[i-1][1] == 1:
#             cur = begin
#             while cur <= stamp:
#                 keyframes.append({"timestamp": cur, "name": rules_text[name], "type": 2, "animation": name})
#                 cur += 1
#             begin = -1
#     if begin != -1: # 如果结束时规则处于触发状态，那么直到结束时每个单位时间都要触发
#         cur = begin
#         while cur <= stamp:
#             keyframes.append({"timestamp": cur, "name": rules_text[name], "type": 2, "animation": name})
#             cur += 1
#     return keyframes



def parse_attribute(name: str, raw_frames: List[RawTraceFrame]) -> List[KeyFrame]:
    keyframes: List[KeyFrame] = []
    for idx in range(len(raw_frames)):
        stamp, value = raw_frames[idx]
        keyframes.append(
            {"timestamp": stamp, "name": name, "type": 1, "animation": str(value)})
    return keyframes


device_prefix = ["door", "fan", "curtain",
                 "airconditioner", "window", "light", 
                 "airpurifier", "robotvacuum", "humidifier",
                 "heater", 'dehumidifier', 'coffeemachine']

def parse_device(name: str, raw_frames: List[RawTraceFrame]) -> List[KeyFrame]:
    keyframes: List[KeyFrame] = []
    keyframes.append({"timestamp": 0, "name": name, "type": 0, "animation": "1" if "door" in name else "0"})
    for idx in range(len(raw_frames)):
        stamp, value = raw_frames[idx]
        if stamp > 0 and (idx == 0 or value != raw_frames[idx-1][1]):
            keyframes.append(
                {"timestamp": stamp, "name": name, "type": 0, "animation": str(int(value))})
    return keyframes


inputs = [
    #("archives/results/2024-09-27-18-28-32-tmp0fd_7945.xml.result", "archives/rules/2024-09-27-18-28-31-tmp0fd_7945_rules.txt_"),
    #("archives/results/2024-09-27-21-47-10-tmpl790avsh.xml.result", "archives/rules/2024-09-27-21-47-09-tmpl790avsh_rules.txt_"),
    #("archives/results/2024-09-27-22-00-56-tmpk5malsfy.xml.result", "archives/rules/2024-09-27-22-00-56-tmpk5malsfy_rules.txt_"),
    #("archives/results/2024-09-27-22-03-21-tmpexpx8oxx.xml.result", "archives/rules/2024-09-27-22-03-21-tmpexpx8oxx_rules.txt_"),
    #("archives/results/2024-09-27-22-31-35-tmp9m4q3xgz.xml.result", "archives/rules/2024-09-27-22-31-34-tmp9m4q3xgz_rules.txt_"),
    #("archives/results/2024-09-27-22-50-03-tmptvy2bghp.xml.result", "archives/rules/2024-09-27-22-50-03-tmptvy2bghp_rules.txt_"),
    
    #("archives/results/2024-10-08-21-51-03-tmptgu_s4qf.xml.result", "archives/rules/2024-10-08-21-51-02-tmptgu_s4qf_rules.txt_")
    #("archives/results/2024-10-08-22-32-32-tmpdbjlzowd.xml.result", "taps/rq3a/case2.txt")
    #("archives/results/2024-10-10-16-33-45-tmpyxo6_lfm.xml.result", "taps/rq3a/case3.txt")
   # ("archives/results/2024-10-11-21-09-46-tmpeiv4cadq.xml.result", "taps/rq3a/case5.txt")
   #("archives/results/2024-10-15-01-07-54-tmpxbpjf28h.xml.result", "taps/rq3a/case6.txt")
   #("archives/results/2024-10-14-18-38-40-tmpj_46jyq0.xml.result", "taps/rq3a/case7.txt")
   #("archives/results/2024-10-15-10-45-42-tmpmqt470t5.xml.result", "taps/rq3a/case10.txt")
   #('archives/results/2024-10-16-10-56-41-tmp419hq9bm.xml.result','taps/rq3a/case11.txt')
    #('archives/results/2024-10-16-11-11-19-tmppp0ifdu6.xml.result','taps/rq3a/case13.txt')
    #('archives/results/2024-10-16-14-56-13-tmpj87mjzl7.xml.result','taps/rq3a/case14.txt')
    ('archives/results/2024-10-16-19-02-18-tmpxdz9v0_b.xml.result','taps/rq3a/case16.txt')
]


if __name__ == "__main__":
    for (trace_input, tap_input) in inputs:
        frames = build_anim_spec(
            open(trace_input, "r").read(), open(tap_input, "r").read())
        frames["keyFrames"].sort(key=lambda x:x["timestamp"])
        open(trace_input + ".json", "w").write(json.dumps(frames, indent=2))
