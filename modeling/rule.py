from loguru import logger
import parse  # type: ignore
from functools import partial

from typing import Dict, List, Tuple
from modeling.common import Composition, PartialComposition, ComposableTemplate
from modeling.human import HumanModel
from modeling.device import device_tables


def build_transition(trigger: str) -> str:
    if "?" in trigger:
        return f'\t\t<label kind="synchronisation">{trigger}</label>\n'
    else:
        return f'\t\t<label kind="guard">{trigger}</label>\n'


def simple_xml_escape(text: str) -> str:
    return text.replace("&&", "&amp;&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_rule(trigger: str, anti_trigger: str, action: str, delay: float, name: str, offset: int) -> PartialComposition:
    # IF "&&" in trigger:
    trigger_list = trigger.split("&&") if "&&" in trigger else [trigger]
    anti_trigger_list = anti_trigger.split(
        "||") if "||" in anti_trigger else [anti_trigger]
    assert len(trigger_list) == len(
        anti_trigger_list), "triggers and anti-triggers does not match"
    state_triggers = list(filter(lambda x: not "?" in x, trigger_list))
    event_triggers = list(filter(lambda x: "?" in x, trigger_list))
    state_anti_triggers = list(
        filter(lambda x: not "?" in x, anti_trigger_list))
    event_anti_triggers = list(filter(lambda x: "?" in x, anti_trigger_list))
    assert len(state_triggers) == len(state_anti_triggers) and len(event_triggers) == len(
        event_anti_triggers), "triggers and anti-triggers does not match"

    vname = name.lower()
    tplt_l, tplt_t = "", ""
    tplt_l += f'\t<location id="id{str(offset)}" x="0" y="0">\n'
    tplt_l += f'\t\t<label kind="invariant">t&lt;={delay}</label>\n'
    tplt_l += f'\t</location>\n'
    tplt_l += f'\t<location id="id{str(offset+1)}" x="150" y="0">\n'
    if len(state_triggers) > 0:
        tplt_l += f'\t\t<committed/>\n'
    tplt_l += f'\t</location>\n'
    tplt_i = f'\t<init ref="id{str(offset)}"/>\n'
    # Build timer edge
    tplt_t += f'\t<transition>\n'
    tplt_t += f'\t\t<source ref="id{str(offset)}"/>\n'
    tplt_t += f'\t\t<target ref="id{str(offset+1)}"/>\n'
    tplt_t += f'\t\t<label kind="guard">t&gt;={delay}</label>\n'
    tplt_t += f'\t\t<label kind="assignment">t=0</label>\n'
    tplt_t += f'\t</transition>\n'
    last_node_offset = 1
    if len(state_triggers) > 0:
        last_node_offset += 1
        tplt_l += f'\t<location id="id{str(offset+2)}" x="300" y="0">\n'
        if len(event_triggers) == 0:
            tplt_l += f'\t\t<committed/>\n'
        tplt_l += f'\t</location>\n'
        # Build state trigger edges
        trigger_guard = simple_xml_escape("&&".join(state_triggers) if len(
            state_triggers) > 1 else state_triggers[0])
        tplt_t += f'\t<transition>\n'
        tplt_t += f'\t\t<source ref="id{str(offset+1)}"/>\n'
        tplt_t += f'\t\t<target ref="id{str(offset+2)}"/>\n'
        tplt_t += f'\t\t<label kind="guard">{trigger_guard}</label>\n'
        if len(event_triggers) == 0:
            tplt_t += f'\t\t<label kind="assignment">{vname}=1,t=0</label>\n'
        tplt_t += f'\t</transition>\n'
        for i, sat in enumerate(state_anti_triggers):
            sat = sat.replace(" ", '')
            tplt_t += f'\t<transition>\n'
            tplt_t += f'\t\t<source ref="id{str(offset+1)}"/>\n'
            tplt_t += f'\t\t<target ref="id{str(offset)}"/>\n'
            tplt_t += f'\t\t<label kind="guard">{simple_xml_escape(sat)}</label>\n'
            tplt_t += f'\t\t<label kind="assignment">{vname}=0,t=0</label>\n'
            tplt_t += f'\t\t<nail x="150" y="{(i+1)*50}"/>\n'
            tplt_t += f'\t\t<nail x="0" y="{(i+1)*50}"/>\n'
            tplt_t += f'\t</transition>\n'
    if len(event_triggers) > 0:
        # Build event trigger edges
        for i, event_trigger in enumerate(event_triggers):
            last_node_offset += 1
            tplt_l += f'\t<location id="id{str(offset+last_node_offset)}" x="{last_node_offset * 150}" y="0">\n'
            tplt_l += f'\t</location>\n'
            tplt_t += f'\t<transition>\n'
            tplt_t += f'\t\t<source ref="id{str(offset+last_node_offset-1)}"/>\n'
            tplt_t += f'\t\t<target ref="id{str(offset+last_node_offset)}"/>\n'
            tplt_t += f'\t\t<label kind="synchronisation">{simple_xml_escape(event_trigger)}</label>\n'
            # Mark the rule as enabled only if the last trigger is fulfilled
            if i == len(event_triggers) - 1:
                tplt_t += f'\t\t<label kind="assignment">{vname}=1,t=0</label>\n'
            tplt_t += f'\t</transition>\n'

    # Build action edge
    tplt_t += f'\t<transition>\n'
    tplt_t += f'\t\t<source ref="id{str(offset+last_node_offset)}"/>\n'
    tplt_t += f'\t\t<target ref="id{str(offset)}"/>\n'
    tplt_t += f'\t\t<label kind="synchronisation">{action}</label>\n'
    tplt_t += f'\t\t<nail x="{last_node_offset * 150}" y="-50"/>\n'
    tplt_t += f'\t\t<nail x="0" y="-50"/>\n'
    tplt_t += f'\t</transition>\n'

    template = ""
    template += f'<template>\n'
    template += f'\t<name>{name}</name>\n'
    template += f'\t<declaration>clock t;</declaration>\n'
    template += tplt_l + tplt_i + tplt_t
    template += f'</template>\n'
    return name, template, f"int {name.lower()};"


trigger_mappings = {
    '{name}_{i}.on': '{name}[{i}]==1',
    '{name}_{i}.off': '{name}[{i}]==0',
    '{name}_{i}.open': '{name}[{i}]==1',
    '{name}_{i}.closed': '{name}[{i}]==0',
    '{name}_{i}.turn_{name}_on': 'turn_on_{name}[{i}]?',
    '{name}_{i}.turn_{name}_off': 'turn_off_{name}[{i}]?',
    '{name}_{i}.open_{name}': 'open_{name}[{i}]?',
    '{name}_{i}.close_{name}': 'close_{name}[{i}]?',
    'rain.start_rain': 'startRain?',
    'rain.stop_rain': 'stopRain?',
    'rain.is_rain': 'rain==1',
    'rain.is_not_rain': 'rain==0',
}

comparisons = ["==", "!=", "<", ">", "<=", ">="]
variables = ["time", "temperature", "pm_2_5"]
for var in variables:
    for cmp in comparisons:
        trigger_mappings[f"{var}{cmp}"+"{val}"] = f"{var}{cmp}"+"{val}"

action_mappings = {
    '{name}_{i}.turn_{name}_on': 'turn_on_{name}[{i}]!',
    '{name}_{i}.turn_{name}_off': 'turn_off_{name}[{i}]!',
    '{name}_{i}.open_{name}': 'open_{name}[{i}]!',
    '{name}_{i}.close_{name}': 'close_{name}[{i}]!',
    'airconditioner_{i}.turn_ac_off': 'turn_ac_off[{i}]!',
    'airconditioner_{i}.turn_ac_cool': 'turn_ac_cool[{i}]!',
    'airconditioner_{i}.turn_ac_heat': 'turn_ac_heat[{i}]!',
    'robotvacuum_{i}.turn_rv_on': 'turn_on_robotvacuum[{i}]!',
    'robotvacuum_{i}.turn_rv_off': 'turn_off_robotvacuum[{i}]!',
    'sms.send_msg': 'send_msg!'
}


on_off_devices_names = [
    "fan", "airpurifier", "light",  "camera", "humidifier", "robotvacuum"
]

open_close_devices_names = [
    "door", "curtain", "window",
]

special_devices_names = [
    "airconditioner", "sms"
]

valid_device_names = on_off_devices_names + \
    open_close_devices_names + special_devices_names


device_to_name: Dict[ComposableTemplate, str] = {
    # TODO: use selected device table
    v: k for k, v in device_tables[list(device_tables.keys())[0]].items()
}

for device_name in valid_device_names:
    # TODO: use selected device table
    assert device_name in device_tables[list(device_tables.keys())[0]].keys(
    ), "no corresponding device:" + device_name + " in " + str(list(device_tables[list(device_tables.keys())[0]].keys(
    )))

# TODO: use selected device table
for device_name in device_tables[list(device_tables.keys())[0]].keys():
    assert device_name in valid_device_names, "device name not valid:" + device_name


def parse_trigger(location_to_idx: Dict[str, int], raw_trigger: str) -> str:
    # Case 1. starts with "Human."
    if raw_trigger.startswith("Human."):
        position_name = raw_trigger.replace("Human.", "")
        return f'humanposition=={location_to_idx[position_name]}'
    else:  # Case 2. in mapping table
        for t_format, inner_format in trigger_mappings.items():
            values = parse.parse(t_format, raw_trigger)
            if values != None:
                if 'name' in values.named.keys():
                    # Sanity check
                    assert values.named['name'] in valid_device_names
                return inner_format.format(**values.named)
    return ""


def parse_rule(location_to_idx: Dict[str, int], trigger: str, action: str) -> Tuple[str, str]:
    inner_t, inner_a = "", ""
    if " AND " in trigger:
        inner_t = " && ".join(
            map(partial(parse_trigger, location_to_idx), trigger.split(" AND ")))
    else:
        inner_t = parse_trigger(location_to_idx, trigger)
    for a_format, inner_format in action_mappings.items():
        values = parse.parse(a_format, action)
        if values != None:
            inner_a = inner_format.format(**values.named)
    assert inner_t != "" and inner_a != "", f"bad rule: {trigger}, {action}: {inner_t}, {inner_a}"
    return inner_t, inner_a


def parse_tap_rules(location_to_idx: Dict[str, int], text: str) -> Tuple[List[str], List[str]]:
    triggers, actions = [], []
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        trigger = line[line.find("IF ") + len("IF "):line.find(" THEN ")]
        action = line[line.find(" THEN ") + len(" THEN "):]
        logger.info(location_to_idx)
        inner_t, inner_a = parse_rule(location_to_idx, trigger, action)
        assert inner_t != None, f"bad trigger: {trigger}, in {text}"
        assert inner_a != None, f"bad action: {action}, in {text}"
        triggers.append(inner_t)
        actions.append(inner_a)
    return triggers, actions


anti_pairs = [
    ["==", "!="], ["<=", ">"], [">=", "<"]
]


def to_anti_trigger(trigger: str) -> str:
    if "&&" in trigger:
        sub_triggers = trigger.split("&&")
        return "||".join(list(map(to_anti_trigger, sub_triggers)))
    elif "?" in trigger:
        return trigger  # DO NOT EDIT EVENT TRIGGER
    else:
        for pair in anti_pairs:
            f, s = pair
            if f in trigger:
                return trigger.replace(f, s)
        for pair in anti_pairs:
            s, f = pair
            if f in trigger:
                return trigger.replace(f, s)
        return ""


assert to_anti_trigger("a>b") == "a<=b"
assert to_anti_trigger("a<=b") == "a>b"
assert to_anti_trigger("a>b&&a<=b") == "a<=b||a>b"


class RuleSet:
    rule_node_number = 10

    def __init__(self, human_model: HumanModel,  raw_text: str, delay: float):
        location_to_idx = {v: i for i, v in enumerate(human_model.locations)}
        self.raw_text = raw_text
        self.rules: List[ComposableTemplate] = []
        tap_rules = zip(*parse_tap_rules(location_to_idx, raw_text))
        for i, (trigger, action) in enumerate(tap_rules):
            self.rules.append(
                ComposableTemplate(f"Rule{i+1}", partial(build_rule, trigger, to_anti_trigger(
                    trigger), action, delay), self.rule_node_number)
            )

    def compose(self, starting_node_id: int) -> Composition:
        t_tplt, t_decl, t_inst, t_sys, t_var = "", "", "", "", ""
        t_used_nodes = 0
        for num, rule in enumerate(self.rules):
            tplt, decl, inst, sys, var, used_nodes = rule.compose(
                starting_node_id + num * self.rule_node_number)
            t_tplt += tplt
            t_decl += decl
            t_inst += inst
            t_sys += sys
            t_var += var
            t_used_nodes += used_nodes
        return t_tplt, t_decl, t_inst, t_sys, t_var, t_used_nodes


# test = RuleSet(HumanModelWithThreeLocations, """IF Human.home THEN door_0.open_door
# IF Human.out THEN light_0.turn_light_off
# IF door_0.open THEN camera_0.turn_camera_on
# IF camera_0.on THEN SMS.send_msg
# IF door_0.open THEN SMS.send_msg
# """, 0.1)
# print(test.compose(100))
# def update_rules(tap_set: str, rule_delay=1):
#     if not os.path.exists(f'rule_templates/{tap_set}'):
#         os.mkdir(f'rule_templates/{tap_set}')
#     tap_rules = zip(
#         *parse_tap_rules(open(f'taps/{tap_set}.txt', "r").read()))
#     for i, (trigger, action) in enumerate(tap_rules):
#         open(f"rule_templates/{tap_set}/rule{i+1}.tplt", "w").write(build_rule(
#             f"Rule{i+1}", trigger, to_anti_trigger(trigger), action, rule_delay, i * 10))


# if __name__ == "__main__":
#     # tap_sets = ['RQ3Case1', 'RQ3Case3', 'RQ3Case4',
#     #             'RQ3Case5', 'RQ3Case6', 'RQ3Case7', 'RQ3Case9', 'RQ3Case10']
#     tap_sets = ["CaseStudy"]
#     for tap_set in tap_sets:
#         update_rules(tap_set)
