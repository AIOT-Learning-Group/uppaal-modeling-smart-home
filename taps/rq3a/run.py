from config import KNOWLEDGEBASE_SYSTEM_DEVICE_MODELS
from modeling.composition import Simulation
from modeling.continuous import build_continuous_template, curve_normal_dist, remap
from modeling.human import HumanModelWithThreeLocationsRQ3A
from modeling.rule import RuleSet, init_global_rule_context
from modeling.device import device_tables, load_device_table

def rq3a_rule_preprocess(rule_path: str) -> str:
    raw_rules = open(rule_path, encoding="utf-8").read()
    rules = []
    for rule in raw_rules.split("\n"):
        if "IF" in rule:
            if rule[rule.find("THEN"):].find("AND") != -1:
                rule1 = rule[rule.find("IF"):rule.rfind("AND")]
                rule2 = rule[rule.find("IF"):rule.find("THEN")] + "THEN" + rule[rule.rfind("AND")+3:]
                rules.append(rule1.strip())
                rules.append(rule2.strip())
            else:
                rules.append(rule[rule.find("IF"):])
    return "\n".join(rules)

from knowledgebase.system_device_models_pb2 import Device as PbDevice, SystemDeviceModels as PbSystemDeviceModels
from google.protobuf import text_format

def test_1():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()
    
    simulation = Simulation(HumanModelWithThreeLocationsRQ3A)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\p1b.txt"))

    points_number = 5
    dpoints = curve_normal_dist(points_number, 24.0, 8.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))

    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))

    device_numbers = {"Door": 2, "Light": 2, "Curtain": 2}

    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\test_model.xml", "w").write(simulation.full_body)

test_1()


