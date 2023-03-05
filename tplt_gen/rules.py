import os
import parse
from tplt_gen.human import locations_ids


def build_rule(name, trigger, anti_trigger, action, delay, offset):
    trigger = trigger.replace("&&", "&amp;&amp;").replace(
        "<", "&lt;").replace(">", "&gt;")
    anti_trigger = anti_trigger.replace("&&", "&amp;&amp;").replace(
        "<", "&lt;").replace(">", "&gt;")
    vname = name.lower()
    template = ""
    template += f'<template>\n'
    template += f'\t<name>{name}</name>\n'
    template += f'\t<declaration>clock t;</declaration>\n'
    template += f'\t<location id="id{str(offset)}" x="0" y="0">\n'
    template += f'\t\t<label kind="invariant">t&lt;={delay}</label>\n'
    template += f'\t</location>\n'
    template += f'\t<location id="id{str(offset+1)}" x="150" y="0">\n'
    template += f'\t\t<committed/>\n'
    template += f'\t</location>\n'
    template += f'\t<location id="id{str(offset+2)}" x="300" y="0">\n'
    template += f'\t\t<committed/>\n'
    template += f'\t</location>\n'

    template += f'\t<init ref="id{str(offset)}"/>\n'

    template += f'\t<transition>\n'
    template += f'\t\t<source ref="id{str(offset)}"/>\n'
    template += f'\t\t<target ref="id{str(offset+1)}"/>\n'
    template += f'\t\t<label kind="guard">t&gt;={delay}</label>\n'
    template += f'\t\t<label kind="assignment">t=0</label>\n'
    template += f'\t</transition>\n'

    template += f'\t<transition>\n'
    template += f'\t\t<source ref="id{str(offset+1)}"/>\n'
    template += f'\t\t<target ref="id{str(offset+2)}"/>\n'
    template += f'\t\t<label kind="guard">{trigger}</label>\n'
    template += f'\t\t<label kind="assignment">{vname}=1,t=0</label>\n'
    template += f'\t</transition>\n'

    template += f'\t<transition>\n'
    template += f'\t\t<source ref="id{str(offset+2)}"/>\n'
    template += f'\t\t<target ref="id{str(offset)}"/>\n'
    template += f'\t\t<label kind="synchronisation">{action}</label>\n'
    template += f'\t\t<nail x="300" y="-50"/>\n'
    template += f'\t\t<nail x="0" y="-50"/>\n'
    template += f'\t</transition>\n'
    if "||" in anti_trigger:
        sub_anti_triggers = anti_trigger.split("||")
        for sat in sub_anti_triggers:
            sat = sat.replace(" ", '')
            template += f'\t<transition>\n'
            template += f'\t\t<source ref="id{str(offset+1)}"/>\n'
            template += f'\t\t<target ref="id{str(offset)}"/>\n'
            template += f'\t\t<label kind="guard">{sat}</label>\n'
            template += f'\t\t<label kind="assignment">{vname}=0,t=0</label>\n'
            template += f'\t\t<nail x="150" y="50"/>\n'
            template += f'\t\t<nail x="0" y="50"/>\n'
            template += f'\t</transition>\n'
    else:
        template += f'\t<transition>\n'
        template += f'\t\t<source ref="id{str(offset+1)}"/>\n'
        template += f'\t\t<target ref="id{str(offset)}"/>\n'
        template += f'\t\t<label kind="guard">{anti_trigger}</label>\n'
        template += f'\t\t<label kind="assignment">{vname}=0,t=0</label>\n'
        template += f'\t\t<nail x="150" y="50"/>\n'
        template += f'\t\t<nail x="0" y="50"/>\n'
        template += f'\t</transition>\n'

    template += f'</template>\n'
    return template

# channel_mappings


trigger_mappings = {
    '{name}_{i}.on': '{name}[{i}]==1',
    '{name}_{i}.off': '{name}[{i}]==0',
    '{name}_{i}.open': '{name}[{i}]==1',
    '{name}_{i}.closed': '{name}[{i}]==0',
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
        assert inner_t != None, f"bad trigger: {trigger}"
        assert inner_a != None, f"bad action: {action}"
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
    tap_sets = ['RQ3Case1', 'RQ3Case3']
    for tap_set in tap_sets:
        if not os.path.exists(f'rule_templates/{tap_set}'):
            os.mkdir(f'rule_templates/{tap_set}')
        tap_rules = zip(
            *parse_tap_rules(open(f'taps/{tap_set}.txt', "r").read()))
        for i, (trigger, action) in enumerate(tap_rules):
            open(f"rule_templates/{tap_set}/rule{i+1}.tplt", "w").write(build_rule(
                f"Rule{i+1}", trigger, to_anti_trigger(trigger), action, rule_delay, i * 10))
