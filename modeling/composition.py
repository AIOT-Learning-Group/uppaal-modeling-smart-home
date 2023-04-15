from modeling.human import HumanModelForSmartHome
from modeling.rule import name_to_device, RuleSet
from modeling.common import ComposableTemplate, Composition, TemplateGenerator
from typing import List, Set
from modeling.human import HumanModelForSmartHome


def filter_interacive_devices_by_rules(tap_rules: str) -> Set[ComposableTemplate]:
    device_set: Set[ComposableTemplate] = set([])
    for name, device in name_to_device.items():
        if name in tap_rules:
            device_set.add(device)
    return device_set


class SystemBehaviorModel:
    header = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' 'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
<nta>
"""
    footer = "</nta>"

    def load_tap_rules(self, tap_rules: str) -> None:
        self.ruleset = RuleSet(HumanModelForSmartHome, tap_rules, 1)
        self.devices_tplt = filter_interacive_devices_by_rules(tap_rules)

    def compose(self, starting_node_id: int = 0) -> None:
        tplt, _, _, _, _, num_nodes = self.ruleset.compose(starting_node_id)
        self.body = tplt
        starting_node_id += num_nodes
        self.devices_composition: List[Composition] = []
        for device in self.devices_tplt:
            device_composition = device.compose(starting_node_id)
            self.body += device_composition[0]
            self.devices_composition.append(device_composition)
            starting_node_id += device.used_nodes
        self.used_nodes = starting_node_id
        self.full_body = self.header + self.body + self.footer


def compose_system_behavior_model(tap_rules: str) -> SystemBehaviorModel:
    model = SystemBehaviorModel()
    model.load_tap_rules(tap_rules)
    model.compose()
    return model


class Simulation(SystemBehaviorModel):
    def compose(self, starting_node_id: int = 0) -> None:
        tplt, _, _, _, _, num_nodes = self.ruleset.compose(starting_node_id)
        self.body = tplt
        starting_node_id += num_nodes
        self.devices_composition: List[Composition] = []
        for device in self.devices_tplt:
            device_composition = device.compose(starting_node_id)
            self.body += device_composition[0]
            self.devices_composition.append(device_composition)
            starting_node_id += device.used_nodes
        self.used_nodes = starting_node_id
        self.full_body = self.header + self.body + self.footer

    def add_tplt_gen(self, tplt_gens: TemplateGenerator) -> None:
        pass

    def run(self) -> str:
        return "Nothing to show."
