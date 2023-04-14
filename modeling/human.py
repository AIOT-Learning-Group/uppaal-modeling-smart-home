from modeling.common import Composition, PartialComposition, ComposableTemplate
from typing import List, Dict


def build_human(locations: List[str], movements: List[str], offset: int = 100) -> PartialComposition:
    location_to_idx = {v: i for i, v in enumerate(locations)}
    name = "HumanPosition"
    occurrence: Dict[str, int] = {}
    template = ""
    template += "<template>\n"
    template += f"\t<name>{name}</name>\n"
    params = ""
    for i in range(len(movements)-1):
        params += f"double t{str(i)}"
        if i < len(movements) - 2:
            params += ","
    template += f"\t<parameter>{params}</parameter>\n"
    template += "\t<declaration>//</declaration>\n"
    template += f'\t<location id="id{str(offset)}" x="150" y="100">\n'
    template += "\t\t<committed/>\n"
    template += "\t</location>\n"
    for i, movement in enumerate(movements):
        if not movement in occurrence.keys():
            occurrence[movement] = 0
        name = movement + "_" + str(occurrence[movement])
        occurrence[movement] += 1
        template += f'\t<location id="id{str(offset+i+1)}" x="{str(150*(i+2))}" y="100">\n'
        template += f'\t\t<name>{name}</name>\n'
        if i < len(movements) - 1:
            template += f'\t\t<label kind="invariant">time&lt;=t{str(i)}</label>\n'
        template += "\t</location>\n"
    template += f'\t<init ref="id{str(offset)}"/>\n'
    for i, movement in enumerate(movements):
        location_id = location_to_idx[movement]
        template += f'\t<transition>\n'
        template += f'\t\t<source ref="id{str(offset+i)}"/>\n'
        template += f'\t\t<target ref="id{str(offset+i+1)}"/>\n'
        if i > 0:
            template += f'\t\t<label kind="guard">time&gt;=t{str(i-1)}</label>\n'
        template += f'\t\t<label kind="assignment">position={location_id}</label>\n'
        template += f'\t</transition>\n'
    template += "</template>\n"
    return "HumanPosition", template, "int humanposition;"


class HumanModel:  # locations：布局，movements: 移动
    def __init__(self, locations: List[str]):
        self.locations = locations

    def compose(self, starting_node_id: int, movements: List[str], raw_params: List[float]) -> Composition:
        assert len(movements) == len(raw_params) + 1
        [name, tplt, decl] = build_human(
            self.locations, movements, starting_node_id)
        params = ",".join([str(i) for i in raw_params])
        inst = f"{name}Model={name}({params});"
        sys = f",{name}Model"
        var = f",{name.lower()}"
        used_nodes = len(movements) + 1
        return tplt, decl, inst, sys, var, used_nodes


HumanModelWithFiveLocations = HumanModel(["out", "l1", "l2", "l3", "l4"])
HumanModelWithThreeLocations = HumanModel(["out", "home", "livingroom"])
HumanModelForSmartHome = HumanModel(
    ["out", "living_room", "kitchen", "bathroom", "bedroom", "guest_room"])
