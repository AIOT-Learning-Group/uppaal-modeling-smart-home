from modeling.composition import Simulation
from modeling.continuous import build_continuous_template, curve_constant, curve_normal_dist, remap, xy_to_points
from modeling.human import HumanModel
from modeling.rule import init_global_rule_context
from modeling.device import load_device_table
from service.simulation import run

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

from knowledgebase.system_device_models_pb2 import SystemDeviceModels as PbSystemDeviceModels
from google.protobuf import text_format

def test_1():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\p1b.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", "bedroom", "out"], [50.0, 150.0, 250.0]))

    points_number = 50
    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))

    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_constant(points_number, 10)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))

    device_numbers = {"Door": 2, "Light": 2, "Curtain": 2}

    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\test_model.xml", "w").write(simulation.full_body)

    run(simulation)

def test_2():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\p2b.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", "bedroom", "out"], [50.0, 150.0, 250.0]))

    points_number = 50
    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))

    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_constant(points_number, 10)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))

    device_numbers = {"Door": 2, "Light": 2, "Curtain": 2}

    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\test_model.xml", "w").write(simulation.full_body)

    run(simulation)

def test_3():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\p3b.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", "bedroom", "out"], [50.0, 150.0, 250.0]))

    points_number = 50
    dpoints = curve_normal_dist(points_number, 20.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))

    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_constant(points_number, 10)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))

    device_numbers = {"Door": 2, "Light": 2, "Curtain": 2}

    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\test_model.xml", "w").write(simulation.full_body)

    run(simulation)

def test_4():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\p4b.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", "bedroom", "out"], [50.0, 150.0, 250.0]))

    points_number = 50
    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))

    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_constant(points_number, 10)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))

    device_numbers = {"Door": 2, "Light": 2, "Curtain": 2}

    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\test_model.xml", "w").write(simulation.full_body)

    run(simulation)

def test_5():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\p5b.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", "bedroom", "out"], [50.0, 150.0, 250.0]))

    points_number = 50
    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))

    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_constant(points_number, 10)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))

    device_numbers = {"Door": 2, "Light": 2, "Curtain": 2}

    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\test_model.xml", "w").write(simulation.full_body)

    run(simulation)

def test_6():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\p6b.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", "bedroom", "out"], [50.0, 150.0, 250.0]))

    points_number = 50
    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))

    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_normal_dist(points_number, 32.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))

    device_numbers = {"Door": 2, "Light": 2, "Curtain": 2}

    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\test_model.xml", "w").write(simulation.full_body)

    run(simulation)

def test_temp():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\p6b.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", "bedroom", "out"], [50.0, 150.0, 250.0]))

    dpoints = xy_to_points([2, 5, 8, 11, 14, 17, 20, 23], [18, 18, 22, 29, 32, 30, 26, 22])
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        dpoints, template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    device_numbers = {"Door": 2, "Light": 2, "Curtain": 2}

    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\test_model.xml", "w").write(simulation.full_body)

#test_temp()

def test_case1():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case1.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", "bedroom", "out"], [50.0, 150.0, 250.0]))

    points_number = 50
    dpoints = curve_normal_dist(points_number, 24.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    simulation.compose(int(sim_time))
    open("taps\\rq3a\\case1.xml", "w").write(simulation.full_body)
    run(simulation)

def test_case2():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case2.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", "bedroom", "out"], [50.0, 150.0, 250.0]))

    points_number = 50
    dpoints = curve_normal_dist(points_number, 12.0, 12.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))
    
    dpoints = curve_normal_dist(points_number, 300.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    simulation.compose(int(sim_time))
    open("taps\\rq3a\\case2.xml", "w").write(simulation.full_body)
    run(simulation)

def test_case3():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case3.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", "bedroom", "out"], [50.0, 150.0, 250.0]))

    points_number = 50
    dpoints = curve_normal_dist(points_number, 9.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))
    
    dpoints = curve_normal_dist(points_number, 300.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case3.xml", "w").write(simulation.full_body)
    run(simulation)

def test_case4():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case4.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", "bathroom", "bedroom", "out"], [50.0, 125.0, 175.0,  250.0]))

    points_number = 50
    dpoints = curve_normal_dist(points_number, 9.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case4.xml", "w").write(simulation.full_body)
    run(simulation)


def test_case5():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case5.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [50.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 9.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))
    
    dpoints = curve_normal_dist(points_number, 300.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case5.xml", "w").write(simulation.full_body)
    run(simulation)


def test_case6():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case6.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [50.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 9.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_constant(points_number, 30)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))
    
    dpoints = curve_normal_dist(points_number, 300.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case6.xml", "w").write(simulation.full_body)
    run(simulation)


def test_case7():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case7.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [50.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 9.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case7.xml", "w").write(simulation.full_body)
    run(simulation)

def test_case8():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case8.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [50.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 9.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4, "Door":2}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case8.xml", "w").write(simulation.full_body)
    run(simulation)


def test_case9():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case9.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [20.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 8.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4, "Door":2, "Window": 2}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case9.xml", "w").write(simulation.full_body)
    run(simulation)

def test_case10():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case10.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [20.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 8.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4, "Door":2, "Window": 2}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case10.xml", "w").write(simulation.full_body)
    run(simulation)

def test_case11():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case11.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [20.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 8.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_normal_dist(points_number, 20.0, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4, "Door":2, "Window": 2}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case11.xml", "w").write(simulation.full_body)
    run(simulation)

def test_case13():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case13.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [20.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 8.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_normal_dist(points_number, 20.0, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4, "Door":2, "Window": 2}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case13.xml", "w").write(simulation.full_body)
    run(simulation)

def test_case12():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case12.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [20.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 8.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_normal_dist(points_number, 20.0, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4, "Door":2, "Window": 2}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case12.xml", "w").write(simulation.full_body)
    run(simulation)


def test_case14():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case14.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [20.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 8.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_normal_dist(points_number, 20.0, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4, "Door":2, "Window": 1}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case14.xml", "w").write(simulation.full_body)
    run(simulation)

def test_case15():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case15.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [20.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 8.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_normal_dist(points_number, 20.0, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4, "Door":2, "Window": 1}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case15.xml", "w").write(simulation.full_body)
    run(simulation)

def test_case16():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case16.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [20.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 8.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_normal_dist(points_number, 20.0, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4, "Door":2, "Window": 2}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case16.xml", "w").write(simulation.full_body)
    run(simulation)


def test_case17():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case17.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [20.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 8.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_normal_dist(points_number, 20.0, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4, "Door":2, "Window": 2}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case17.xml", "w").write(simulation.full_body)
    run(simulation)

def test_case18():
    pb_system_device_models = PbSystemDeviceModels()
    text_format.Parse(open("taps\\rq3a\\system_device_models_rq3a.textproto",
                  'r').read(), pb_system_device_models)
    load_device_table(pb_system_device_models)

    init_global_rule_context()

    human = HumanModel(["out", "living_room", "bedroom", 'kitchen', "bathroom"])
    
    simulation = Simulation(human)
    sim_time = 300
    simulation.load_tap_rules(rq3a_rule_preprocess(f"taps\\rq3a\\case18.txt"))

    simulation.add_tplt_gen(lambda x: human.compose(x, ["out", "living_room", 'kitchen',"bathroom", "bedroom", "out"], [20.0, 100.0, 150.0, 200.0, 250.0]))
    points_number = 50
    dpoints = curve_normal_dist(points_number, 8.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    
    dpoints = curve_normal_dist(points_number, 20, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentHumidity",
        clock_name="time", var_name="humidity", offset=x))
    
    dpoints = curve_normal_dist(points_number, 48.0, 24.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentAirquality",
        clock_name="time", var_name="airquality", offset=x))

    dpoints = curve_normal_dist(points_number, 100.0, 240.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentPM25",
        clock_name="time", var_name="pm25", offset=x))

    dpoints = curve_normal_dist(points_number, 20.0, 50.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentCO",
        clock_name="time", var_name="co", offset=x))
    
    dpoints = curve_normal_dist(points_number, 200.0, 1200.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentBrightness",
        clock_name="time", var_name="brightness", offset=x))

    device_numbers = {"Curtain": 2, "Light": 4, "Door":2, "Window": 1}
    simulation.compose(int(sim_time), device_numbers)
    open("taps\\rq3a\\case18.xml", "w").write(simulation.full_body)
    run(simulation)

test_case18()
