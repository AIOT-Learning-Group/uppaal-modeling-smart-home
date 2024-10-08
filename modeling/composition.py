from loguru import logger
from modeling.human import HumanModel, HumanModelForSmartHome
from modeling.rule import RuleSet
from modeling.device import device_tables
from modeling.common import ComposableTemplate, Composition, TemplateGenerator
from typing import List, Set
from modeling.human import HumanModelForSmartHome


def filter_interacive_devices_by_rules(tap_rules: str) -> Set[ComposableTemplate]:
    device_set: Set[ComposableTemplate] = set([])
    # TODO: use selected device table
    logger.info(f"device list: {[name for name, _ in device_tables[list(device_tables.keys())[0]].items()]}")
    for name, device in device_tables[list(device_tables.keys())[0]].items():
        if f" {name}_" in tap_rules:
            device_set.add(device)
            logger.info(f"filter device: {name}")
    return device_set


header = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' 'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
<nta>
"""
footer = "</nta>"


class SystemBehaviorModel:
    def load_tap_rules(self, tap_rules: str) -> None:
        self.ruleset = RuleSet(HumanModelForSmartHome, tap_rules, 1)
        self.devices_tplt = filter_interacive_devices_by_rules(tap_rules)

    def compose(self, starting_node_id: int = 0) -> None:
        tplt, _, _, _, _, num_nodes = self.ruleset.compose(starting_node_id)
        self.body = tplt
        starting_node_id += num_nodes
        self.devices_composition: List[Composition] = []
        print("devices:", len(self.devices_tplt))
        for device in self.devices_tplt:
            device_composition = device.compose(starting_node_id)
            
            self.body += device_composition[0]
            print("dcp:", device_composition[1])
            self.devices_composition.append(device_composition)
            starting_node_id += device.used_nodes
        
        self.used_nodes = starting_node_id
        self.full_body = header + self.body + footer


def compose_system_behavior_model(tap_rules: str) -> SystemBehaviorModel:
    model = SystemBehaviorModel()
    model.load_tap_rules(tap_rules)
    model.compose()
    return model


class Simulation:
    def __init__(self, human_model: HumanModel = HumanModelForSmartHome) -> None:
        self.tplt, self.decl, self.inst, self.sys, self.var = "", "", "", "", ""
        self.human_model = human_model
        self.starting_node_id = 0

    def load_tap_rules(self, tap_rules: str) -> None:
        self.raw_rules = tap_rules
        self.ruleset = RuleSet(self.human_model, tap_rules, 1)
        self.devices_tplt = filter_interacive_devices_by_rules(tap_rules)

    def accumulate(self, composition: Composition) -> int:
        tplt, decl, inst, sys, var, num_nodes = composition
        self.tplt += tplt
        self.decl += decl
        self.inst += inst
        self.sys += sys
        self.var += var
        return num_nodes

    def add_tplt_gen(self, tplt_gen: TemplateGenerator) -> None:
        num_nodes = self.accumulate(tplt_gen(self.starting_node_id))
        self.starting_node_id += num_nodes

    def compose(self, duration: int, device_numbers: dict[str, int] | None = None) -> None:
        num_nodes = self.accumulate(
            self.ruleset.compose(self.starting_node_id))
        self.starting_node_id += num_nodes
        self.devices_composition: List[Composition] = []
        for device in self.devices_tplt:
            device_number = 1
            if device_numbers != None and device.name in device_numbers.keys():
                device_number = device_numbers[device.name]
            num_nodes = self.accumulate(device.compose(
                self.starting_node_id, device_number))
            logger.info(f"device instance: {device.name} -> {device_number}")
            self.starting_node_id += num_nodes

        self.body = ""
        # build declaration
        self.body += f'<declaration>// Place global declarations here.\n'
        self.body += "clock time=0.0;" + self.decl
        self.body += f'</declaration>\n'
        # build templates
        self.body += self.tplt
        # build system
        self.sys = self.sys[1:]
        self.body += f'\t<system>\n'
        self.body += self.inst
        self.body += f'system {self.sys};\n'
        self.body += f'</system>\n'
        # build query
        self.var = self.var[1:]
        self.body += f'<queries>\n'
        self.body += f'\t<query>\n'
        self.body += f'\t\t<formula>simulate[&lt;={duration}] {{{self.var}}}</formula>\n'
        self.body += f'\t\t<comment></comment>\n'
        self.body += f'\t</query>\n'
        self.body += f'</queries>\n'

        self.full_body = header + self.body + footer
