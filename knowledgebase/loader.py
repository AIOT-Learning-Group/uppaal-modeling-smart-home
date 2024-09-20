

from typing import Dict, Optional, Union
from modeling.common import PartialComposition, ComposableTemplate, PartialTemplateGenerator, Composition
from .kbeditor.system_device_model_editor_pb2 import DomainEntry
import json
import xml.etree.ElementTree as ET
from google.protobuf.json_format import ParseDict, MessageToJson
from loguru import logger

def update_device_uppaal_file(name: str):
    raw_base: dict = json.loads(open("knowledgebase/kbeditor/SystemDeviceModels_.json").read())
    pb_base = ParseDict(raw_base, DomainEntry(), True)
    for device in pb_base.devices:
        print(device.deviceInfo.name)
        if (device.deviceInfo.name == name):
            device.TAInfo.rawData = open(f"knowledgebase\kbeditor\{device.deviceInfo.name}.xml", "r").read()
    open("knowledgebase/kbeditor/SystemDeviceModels_.json", "w").write(MessageToJson(pb_base))
    

def load_system_device_model():
    raw_base: dict = json.loads(open("knowledgebase/kbeditor/SystemDeviceModels_.json").read())
    print(raw_base.keys())
    pb_base = ParseDict(raw_base, DomainEntry(), True)
    print(pb_base.name)
    for device in pb_base.devices:
        # if (device.deviceInfo.name == "Kohler Bathtub"):
        #     update_device_uppaal_file(device.deviceInfo.name)
        # open(f"knowledgebase\kbeditor\{device.deviceInfo.name}.xml", "w").write(device.TAInfo.rawData)
        update_device_uppaal_file(device.deviceInfo.name)
        # parse_uppaal_format(device.TAInfo.rawData)
        # break

def load_into_device_table(device_tables: Dict[str, Dict[str, ComposableTemplate]]) -> None:
    raw_base: dict = json.loads(open("knowledgebase/kbeditor/SystemDeviceModels.json").read())
    pb_base = ParseDict(raw_base, DomainEntry(), True)
    for device in pb_base.devices:
        result = parse_uppaal_format(device.TAInfo.rawData)
        if result != None:
            logger.info(f"add device from kb: {result.name}")
            device_tables["Smart Home Devices"][result.name.lower()] = result
        else:
            logger.info(f"fail: {device.TAInfo.name}")
        # if (device.deviceInfo.name == "Kohler Bathtub"):
        #     result = parse_uppaal_format(device.TAInfo.rawData)
        #     if result:
        #         # TODO: use real name
        #         device_tables["Smart Home Devices"]["bathtub"] = result

def parse_decl(decl_text: str) -> str:
    decls = list(filter(lambda x: x.endswith("[N];"), decl_text.split("\n")))
    decls = list(map(lambda x: x.replace("[N];", "[{number}];"), decls))
    return "\n".join(decls)


def replace_id(node: ET.Element, name: str, offset: int) -> None:
    assert name in node.keys(), f"found {node.tag} without {name}"
    id_value = int(node.get(name, "").replace("id", ""))
    node.set(name, "id" + str(id_value + offset))

def remap_tplt_ids(tplt: ET.Element, offset: int) -> ET.Element:
    # Find minimum id
    min_id = 0
    for child in tplt:
        if child.tag == "location":
            assert "id" in child.keys(), "found location without id"
            id_value = child.get("id", "").replace("id", "")
            assert id_value.isdigit()
            min_id = min(min_id, int(id_value))
    # Replace for all elements
    for child in tplt:
        if child.tag == "location":
            replace_id(child, "id", offset - min_id)
        if child.tag == "init":
            replace_id(child, "ref", offset - min_id)
        if child.tag == "transition":
            for subchild in child:
                if subchild.tag == "source" or subchild.tag == "target":
                    replace_id(subchild, "ref", offset - min_id)
    return tplt

def extract_inst_params(raw_sys: str, name: str) -> str:
    for inst_def in raw_sys.split("\n"):
        if name in inst_def and not inst_def.startswith("system "):
            prefix = "(0"
            return inst_def[inst_def.find(prefix) + len(prefix):inst_def.find(")")]
    return ""

def compose(decl: str, tplt: ET.Element, raw_sys:str) -> ComposableTemplate:
    name = ""
    used_nodes = 0
    for child in tplt:
        if child.tag == "name" and child.text:
            name = child.text
        elif child.tag == "location":
            used_nodes += 1

    def template_generator(_: str, offset: int) -> PartialComposition:
        print("call template_generator")
        remap_tplt_ids(tplt, offset)
        return name, str(ET.tostring(remap_tplt_ids(tplt, offset)), encoding='utf-8'), decl

    return ComposableTemplateWithParams(name, template_generator, used_nodes + 1, extract_inst_params(raw_sys, name))

class ComposableTemplateWithParams(ComposableTemplate):
    def __init__(self, name: str, template_generator: PartialTemplateGenerator, used_nodes: int, inst_params: str):
        super().__init__(name, template_generator, used_nodes)
        self.inst_params = inst_params

    def compose(self, starting_node_id: int, instance_number: Union[None, int] = None) -> Composition:
        [name, tplt, decl] = self.generator(self.name, starting_node_id)
        inst = ""
        sys = ""
        var = ""
        if "{number}" in decl and type(instance_number) == int:
            decl = decl.format(number=instance_number)
            for i in range(instance_number):
                inst += f"{name}{i}={name}({i}{self.inst_params});"
                sys += f",{name}{i}"
                var += f",{name.lower()}[{i}]"
        else:
            sys = f",{name}"
            var = f",{name.lower()}"
        return tplt, decl, inst, sys, var, self.used_nodes

def parse_uppaal_format(data: str) -> Optional[ComposableTemplate]:
    decl, tplt, raw_sys = None, None, None
    tree = ET.fromstring(data)
    for child in tree:
        if child.tag == "declaration" and child.text:
            decl = parse_decl(child.text)
        elif child.tag == "template":
            tplt = child
        elif child.tag == "system":
            raw_sys = child.text
    if decl and tplt and raw_sys:
        return compose(decl, tplt, raw_sys)
    else:
        logger.info(f"decl: {decl}")
        logger.info(f"tplt: {tplt}")
        logger.info(f"raw_sys: {raw_sys}")
        return None

device_tables: Dict[str, Dict[str, ComposableTemplate]] = {}

if __name__ == "__main__":
    load_system_device_model()