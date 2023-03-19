from modeling.common import Composition, PartialComposition, ComposableTemplate
from typing import List, Dict


def build_human(locations: List[str], offset: int = 100) -> PartialComposition:
    location_to_idx = {v: i for i, v in enumerate(locations)}
    name = "HumanPosition"
    occurrence: Dict[str, int] = {}
    template = ""
    template += "<template>\n"
    template += f"\t<name>{name}</name>\n"
    params = ""
    for i in range(len(locations)-1):
        params += f"double t{str(i)}"
        if i < len(locations) - 2:
            params += ","
    template += f"\t<parameter>{params}</parameter>\n"
    template += "\t<declaration>//</declaration>\n"
    template += f'\t<location id="id{str(offset)}" x="150" y="100">\n'
    template += "\t\t<committed/>\n"
    template += "\t</location>\n"
    for i in range(len(locations)):
        if not locations[i] in occurrence.keys():
            occurrence[locations[i]] = 0
        name = locations[i] + "_" + str(occurrence[locations[i]])
        occurrence[locations[i]] += 1
        template += f'\t<location id="id{str(offset+i+1)}" x="{str(150*(i+2))}" y="100">\n'
        template += f'\t\t<name>{name}</name>\n'
        if i < len(locations) - 1:
            template += f'\t\t<label kind="invariant">time&lt;=t{str(i)}</label>\n'
        template += "\t</location>\n"
    template += f'\t<init ref="id{str(offset)}"/>\n'
    for i in range(len(locations)):
        location_id = location_to_idx[locations[i]]
        template += f'\t<transition>\n'
        template += f'\t\t<source ref="id{str(offset+i)}"/>\n'
        template += f'\t\t<target ref="id{str(offset+i+1)}"/>\n'
        if i > 0:
            template += f'\t\t<label kind="guard">time&gt;=t{str(i-1)}</label>\n'
        template += f'\t\t<label kind="assignment">position={location_id}</label>\n'
        template += f'\t</transition>\n'
    template += "</template>\n"
    return "HumanPosition", template, "int humanposition;"


class HumanModel:
    def __init__(self, locations: List[str]):
        self.locations = locations
        self.used_nodes = len(locations)

    def compose(self, starting_node_id: int, raw_params: List[float]) -> Composition:
        [name, tplt, decl] = build_human(self.locations, starting_node_id)
        params = ",".join([str(i) for i in raw_params])
        inst = f"{name}Model={name}({params});"
        sys = f",{name}Model"
        var = f",{name.lower()}"
        return tplt, decl, inst, sys, var


HumanModelWithFiveLocations = HumanModel(["out", "l1", "l2", "l3", "l4"])
HumanModelWithThreeLocations = HumanModel(["out", "home", "livingroom"])
HumanModelForSmartHome = HumanModel(
    ["out", "living_room", "kitchen", "bathroom", "bedroom", "guest_room"])
