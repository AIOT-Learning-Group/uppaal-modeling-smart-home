import os
import parse
from tplt_gen.human import locations_ids


def build_transition(trigger: str) -> str:
    if "?" in trigger:
        return f'\t\t<label kind="synchronisation">{trigger}</label>\n'
    else:
        return f'\t\t<label kind="guard">{trigger}</label>\n'


def simple_xml_escape(text: str) -> str:
    return text.replace("&&", "&amp;&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_rule(name, trigger, anti_trigger, action, delay, offset):
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
    return template

# channel_mappings


trigger_mappings = {
    '{name}_{i}.on': '{name}[{i}]==1',
    '{name}_{i}.off': '{name}[{i}]==0',
    '{name}_{i}.open': '{name}[{i}]==1',
    '{name}_{i}.closed': '{name}[{i}]==0',
    '{name}_{i}.turn_{name}_on': 'turn_on_{name}[{i}]?',
    '{name}_{i}.turn_{name}_off': 'turn_off_{name}[{i}]?',
    '{name}_{i}.open_{name}': 'open_{name}[{i}]?',
    '{name}_{i}.close_{name}': 'close_{name}[{i}]?',
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
    'ac_{i}.turn_ac_off': 'turn_ac_off[{i}]!',
    'ac_{i}.turn_ac_cool': 'turn_ac_cool[{i}]!',
    'ac_{i}.turn_ac_heat': 'turn_ac_heat[{i}]!',
    'SMS.send_msg': 'send_msg!'
}

valid_device_names = [
    'SMS', 'fan', 'airpurifier', 'door', 'light', 'curtain', 'camera', 'humidifier', 'window'
]


def parse_trigger(raw_trigger: str) -> str:
    # Case 1. starts with "Human."
    if raw_trigger.startswith("Human."):
        position_name = raw_trigger.replace("Human.", "")
        return f'position=={locations_ids[position_name]}'
    else:  # Case 2. in mapping table
        for t_format, inner_format in trigger_mappings.items():
            values = parse.parse(t_format, raw_trigger)
            if values != None:
                if 'name' in values.named.keys():
                    # Sanity check
                    assert values.named['name'] in valid_device_names
                return inner_format.format(**values.named)
    return ""


def parse_rule(trigger: str, action: str):
    inner_t, inner_a = None, None
    if " AND " in trigger:
        inner_t = " && ".join(
            map(parse_trigger, trigger.split(" AND ")))
    else:
        inner_t = parse_trigger(trigger)
    for a_format, inner_format in action_mappings.items():
        values = parse.parse(a_format, action)
        if values != None:
            inner_a = inner_format.format(**values.named)
    return inner_t, inner_a


def parse_tap_rules(text: str):
    triggers, actions = [], []
    for line in text.splitlines():
        trigger = line[line.find("IF ") + len("IF "):line.find(" THEN ")]
        action = line[line.find(" THEN ") + len(" THEN "):]
        inner_t, inner_a = parse_rule(trigger, action)
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

if __name__ == "__main__":
    rule_delay = 1
    # tap_sets = ['RQ3Case1', 'RQ3Case3', 'RQ3Case4',
    #             'RQ3Case5', 'RQ3Case6', 'RQ3Case7', 'RQ3Case9', 'RQ3Case10']
    tap_sets = ["test_state_event"]
    for tap_set in tap_sets:
        if not os.path.exists(f'rule_templates/{tap_set}'):
            os.mkdir(f'rule_templates/{tap_set}')
        tap_rules = zip(
            *parse_tap_rules(open(f'taps/{tap_set}.txt', "r").read()))
        for i, (trigger, action) in enumerate(tap_rules):
            open(f"rule_templates/{tap_set}/rule{i+1}.tplt", "w").write(build_rule(
                f"Rule{i+1}", trigger, to_anti_trigger(trigger), action, rule_delay, i * 10))
