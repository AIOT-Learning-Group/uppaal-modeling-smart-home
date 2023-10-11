import json
from typing import List, Optional

from loguru import logger
from knowledgebase.animation_asset_base_pb2 import AnimationAssetBase, AppearanceStateMachine, AppearanceState, AppearanceTransition
from google.protobuf import text_format

from . import build_anim_spec
from .common import KeyFrame


def parse_state_machine():
    base = AnimationAssetBase()
    text_format.Parse(open("knowledgebase/animation_asset_base.textproto",
                           'r').read(), base)
    machine = base.appearance_state_machine[0]
    return machine


def find_transition(machine: AppearanceStateMachine, state_u: AppearanceState, state_v: AppearanceState) -> Optional[AppearanceTransition]:
    for tran in machine.transitions:
        if tran.prev_state_name == state_u.name and tran.next_state_name == state_v.name:
            return tran
    return None


def find_state_machine(base: AnimationAssetBase, name: str):
    for machine in base.appearance_state_machine:
        if machine.name == name:
            return machine


def to_transition_id(machine: AppearanceStateMachine, tran: AppearanceTransition):
    for (idx, tran_) in enumerate(machine.transitions):
        if tran == tran_:
            return idx


def insert_frames(keyframes: List[KeyFrame], base: AnimationAssetBase):
    inserted_frames = []
    for idx, frame in enumerate(keyframes):
        inserted_frames.append(frame)
        if idx < len(keyframes) - 1:
            flag = frame["type"] == 0 and keyframes[idx + 1]["type"] == 0
            flag = flag and frame["name"] == keyframes[idx + 1]["name"]
            flag = flag and frame["animation"] != keyframes[idx + 1]["animation"]
            if flag:
                logger.info(f'insert frame for {frame["name"]}')
                state_machine = find_state_machine(base, frame["name"])
                if state_machine == None:
                    logger.info(
                        f'state machine not found, skipped')
                    continue
                logger.info(f'find state machine')
                state_u = state_machine.states[int(frame["animation"])]
                logger.info(f'prev_state: {state_u.name}')
                state_v = state_machine.states[int(
                    keyframes[idx + 1]["animation"])]
                logger.info(f'next_state: {state_v.name}')
                tran = to_transition_id(
                    state_machine, find_transition(state_machine, state_u, state_v))
                logger.info(
                    f'tran_id: {tran}, prefab_name: {state_machine.transitions[tran].prefab_name}')
                inserted_frames.append(
                    {'type': 4, 'name': frame["name"], "animation": tran, "timestamp": (
                        frame["timestamp"] + keyframes[idx + 1]["timestamp"]) / 2}
                )
    return inserted_frames


if __name__ == "__main__":
    trace_input = "models/rq3_case_10.xml.result"
    tap_input = "taps/RQ3Case10.txt"
    base = AnimationAssetBase()
    text_format.Parse(open("knowledgebase/animation_asset_base.textproto",
                           'r').read(), base)
    frames = build_anim_spec(
        open(trace_input, "r").read(), open(tap_input, "r").read())["keyFrames"]
    print(len(frames))
    inserted = insert_frames(frames, base)
    print(len(inserted))
    open(trace_input + "_inserted.json",
         "w").write(json.dumps(inserted, indent=2))
