
import re
import os
from tplt_gen.human import build_human
import subprocess


def build_query(time, variables):
    template = ""
    template += f'<queries>\n'
    template += f'\t<query>\n'
    template += f'\t\t<formula>simulate[&lt;={time}] {{{", ".join(variables)}}}</formula>\n'
    template += f'\t\t<comment></comment>\n'
    template += f'\t</query>\n'
    template += f'</queries>\n'
    return template


def build_global_declaration(declarations):
    template = ""
    template += f'<declaration>// Place global declarations here.\n'
    template += declarations
    template += f'</declaration>\n'
    return template


def simulate(model_path, result_path):
    cmd = f"cmd /c verifyta.exe -O std {model_path} > {result_path}".split(" ")
    print(" ".join(cmd))
    result = subprocess.run(
        cmd, cwd="D:\\Workspace\\TapSim\\uppaal-4.1.24\\bin-Windows", stdout=subprocess.PIPE)


def get_tlpt_name(tlpt: str) -> str:
    result = re.findall('<name( x="[\\d]+" y="[\\d]+")?>(\\w+)<\\/name>', tlpt)
    if len(result[0]) == 2:
        return result[0][1]
    else:
        return result[0][0]


def build_system(envs_tplt, devices_tplt, rule_num, moving_time):
    template = ""
    template += f'\t<system>HumanInstance=Human({",".join(list(map(lambda x: str(x), moving_time)))});\n'
    for device in devices_tplt:
        name = get_tlpt_name(device)
        if name == "SMS":
            continue
        else:
            template += f'{name}_0 = {name}(0);\n'
    template += f'system HumanInstance, {", ".join(list(map(lambda x: x+"_0" if x != "SMS" else x, map(get_tlpt_name, devices_tplt))))}, {", ".join(list(map(get_tlpt_name, envs_tplt)))}, {", ".join(f"Rule{i+1}" for i in range(rule_num))};\n'.replace(", , ", ", ")
    template += f'</system>\n'
    return template


def find_env_name(tplt: str) -> str:
    if "EnvironmentTemperature" in tplt:
        return "temperature"
    elif "EnvironmentPM25" in tplt:
        return "pm_2_5"
    elif "EnvironmentHumidity" in tplt:
        return "humidity"
    elif "EnvironmentRain" in tplt:
        return "rain"
    else:
        return None


class Simulatable:
    header = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' 'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
<nta>
"""
    footer = "</nta>"
    envs_tplt = []
    envs_init = {}
    rules_tplt = []
    devices_tplt = []
    locations = []
    moving_time = []
    simulation_time = 30
    full_body = None

    def build(self):
        self.body = ""
        declarations = "clock time;int position=0;"

        for i in range(len(self.rules_tplt)):
            declarations += f"int rule{i+1}=0;\n"
        declarations += open("device_templates/decl", "r").read()
        envs = list(map(find_env_name, self.envs_tplt))
        for env in envs:
            if env != "rain":
                declarations += f"clock {env}={self.envs_init[env]};"
                declarations += f"double d{env}=0.0;"

        assert len(self.locations) == len(self.moving_time) + \
            1, "bad locations or moving time"
        self.body += build_global_declaration(declarations)
        # print(self.body)
        self.body += build_human(self.locations, offset=100)
        for device in self.devices_tplt:
            self.body += device
        for rule in self.rules_tplt:
            self.body += rule
        for env in self.envs_tplt:
            self.body += env
        self.body += build_system(self.envs_tplt, self.devices_tplt,
                                  len(self.rules_tplt), self.moving_time)
        vars = list(map(find_env_name, self.envs_tplt))
        vars += list(map(get_tlpt_name, self.rules_tplt))
        vars += list(map(lambda x: x + "[0]" if x != "SMS" else "received_msgs",
                     map(get_tlpt_name, self.devices_tplt)))
        vars = list(map(lambda x: x.lower(), vars))
        vars += ["position"]
        self.body += build_query(self.simulation_time, vars)
        self.full_body = self.header + self.body + self.footer


def build_RQ3_case_test():
    model = Simulatable()
    model.envs_init['temperature'] = 18.0
    model.envs_tplt.append(
        open('env_templates/temperature.tplt', 'r').read())
    model.rules_tplt.append(
        open('rule_templates/Case2/rule1.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Fan_210.tplt', 'r').read())
    model.locations = ["out", "doorway", "home"]
    model.moving_time = ["10.0", "20.0"]
    model.build()
    model_path = "models/rq3_case_test.xml"
    open(model_path, "w").write(model.full_body)
    simulate(os.path.abspath(model_path),
             os.path.abspath(model_path + ".result"))


def count_tplts(path: str) -> int:
    count = 0
    for sub_path in os.listdir(path):
        if os.path.isfile(os.path.join(path, sub_path)):
            count += 1
    return count


def build_RQ3_case_1():
    model = Simulatable()
    model.simulation_time = 300
    model.envs_init['temperature'] = 18.0
    model.envs_tplt.append(
        open('env_templates/temperature.tplt', 'r').read())
    for i in range(count_tplts("rule_templates/RQ3Case1")):
        model.rules_tplt.append(
            open(f'rule_templates/RQ3Case1/rule{i+1}.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/AirConditioner_230.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Door_240.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Window_290.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/SMS_300.tplt', 'r').read())
    model.locations = ["out", "doorway", "home"]
    model.moving_time = [100.0, 200.0]
    model.build()
    model_path = "models/rq3_case_1.xml"
    open(model_path, "w").write(model.full_body)
    simulate(os.path.abspath(model_path),
             os.path.abspath(model_path + ".result"))


def build_RQ3_case_3():
    model = Simulatable()
    model.simulation_time = 300
    for i in range(count_tplts("rule_templates/RQ3Case3")):
        model.rules_tplt.append(
            open(f'rule_templates/RQ3Case3/rule{i+1}.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Camera_270.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/SMS_300.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Door_240.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Light_250.tplt', 'r').read())
    model.locations = ["out", "doorway", "home"]
    model.moving_time = [100.0, 200.0]
    model.build()
    model_path = "models/rq3_case_3.xml"
    open(model_path, "w").write(model.full_body)
    simulate(os.path.abspath(model_path),
             os.path.abspath(model_path + ".result"))


def build_RQ3_case_4():
    model = Simulatable()
    model.simulation_time = 300
    model.envs_init['temperature'] = 18.0
    model.envs_tplt.append(
        open('env_templates/temperature.tplt', 'r').read())
    for i in range(count_tplts("rule_templates/RQ3Case4")):
        model.rules_tplt.append(
            open(f'rule_templates/RQ3Case4/rule{i+1}.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/AirConditioner_230.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Light_250.tplt', 'r').read())
    model.locations = ["out", "doorway", "home", "out"]
    model.moving_time = [20.0, 40.0, 200.0]
    model.build()
    model_path = "models/rq3_case_4.xml"
    open(model_path, "w").write(model.full_body)
    simulate(os.path.abspath(model_path),
             os.path.abspath(model_path + ".result"))


def build_RQ3_case_5():
    model = Simulatable()
    model.simulation_time = 300
    model.envs_init['temperature'] = 18.0
    model.envs_tplt.append(
        open('env_templates/temperature.tplt', 'r').read())
    for i in range(count_tplts("rule_templates/RQ3Case5")):
        model.rules_tplt.append(
            open(f'rule_templates/RQ3Case5/rule{i+1}.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/AirConditioner_230.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Door_240.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Window_290.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/SMS_300.tplt', 'r').read())
    model.locations = ["out", "doorway", "home"]
    model.moving_time = [5.0, 10.0]
    model.build()
    model_path = "models/rq3_case_5.xml"
    open(model_path, "w").write(model.full_body)
    simulate(os.path.abspath(model_path),
             os.path.abspath(model_path + ".result"))


def build_RQ3_case_6():
    model = Simulatable()
    model.simulation_time = 300
    model.envs_init['temperature'] = 18.0
    model.envs_tplt.append(
        open('env_templates/temperature.tplt', 'r').read())
    model.envs_init['pm_2_5'] = 30.0
    model.envs_tplt.append(
        open('env_templates/pm_2_5.tplt', 'r').read())
    model.envs_init['humidity'] = 12.0
    model.envs_tplt.append(
        open('env_templates/humidity.tplt', 'r').read())
    for i in range(count_tplts("rule_templates/RQ3Case6")):
        model.rules_tplt.append(
            open(f'rule_templates/RQ3Case6/rule{i+1}.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/AirConditioner_230.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Door_240.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Humidifier_280.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/AirPurifier_220.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Curtain_260.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Window_290.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/SMS_300.tplt', 'r').read())
    model.locations = ["out", "doorway", "home"]
    model.moving_time = [100.0, 200.0]
    model.build()
    model_path = "models/rq3_case_6.xml"
    open(model_path, "w").write(model.full_body)
    simulate(os.path.abspath(model_path),
             os.path.abspath(model_path + ".result"))


def build_RQ3_case_7():
    model = Simulatable()
    model.simulation_time = 300
    for i in range(5):
        model.rules_tplt.append(
            open(f'rule_templates/RQ3Case7/rule{i+1}.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Camera_270.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/SMS_300.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Door_240.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Light_250.tplt', 'r').read())
    model.locations = ["out", "doorway", "home"]
    model.moving_time = [200.0, 250.0]
    model.build()
    model_path = "models/rq3_case_7.xml"
    open(model_path, "w").write(model.full_body)
    simulate(os.path.abspath(model_path),
             os.path.abspath(model_path + ".result"))


def build_RQ3_case_9():
    model = Simulatable()
    model.simulation_time = 300
    model.envs_init['temperature'] = 18.0
    model.envs_tplt.append(
        open('env_templates/temperature.tplt', 'r').read())
    for i in range(count_tplts("rule_templates/RQ3Case9")):
        model.rules_tplt.append(
            open(f'rule_templates/RQ3Case9/rule{i+1}.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/AirConditioner_230.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Light_250.tplt', 'r').read())
    model.locations = ["home", "doorway", "out"]
    model.moving_time = [100.0, 200.0]
    model.build()
    model_path = "models/rq3_case_9.xml"
    open(model_path, "w").write(model.full_body)
    simulate(os.path.abspath(model_path),
             os.path.abspath(model_path + ".result"))


def build_RQ3_case_10():
    model = Simulatable()
    model.envs_init['temperature'] = 18.0
    model.envs_init['rain'] = 0
    model.simulation_time = 300
    for i in range(count_tplts("rule_templates/RQ3Case10")):
        model.rules_tplt.append(
            open(f'rule_templates/RQ3Case10/rule{i+1}.tplt', 'r').read())
    model.envs_tplt.append(
        open('env_templates/temperature.tplt', 'r').read())
    model.envs_tplt.append(
        open('device_templates/Rain_310.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Window_290.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Fan_210.tplt', 'r').read())
    model.locations = ["home", "doorway", "out"]
    model.moving_time = [100.0, 200.0]
    model.build()
    model_path = "models/rq3_case_10.xml"
    open(model_path, "w").write(model.full_body)
    simulate(os.path.abspath(model_path),
             os.path.abspath(model_path + ".result"))


def build_RQ3_case_test2():
    model = Simulatable()
    model.simulation_time = 300
    for i in range(count_tplts("rule_templates/test_state_event")):
        model.rules_tplt.append(
            open(f'rule_templates/test_state_event/rule{i+1}.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Light_250.tplt', 'r').read())
    model.locations = ["home", "doorway", "out"]
    model.moving_time = [100.0, 200.0]
    model.build()
    model_path = "models/rq3_case_test2.xml"
    open(model_path, "w").write(model.full_body)
    simulate(os.path.abspath(model_path),
             os.path.abspath(model_path + ".result"))


def build_case_study():

    import tplt_gen.human
    tplt_gen.human.locations_ids = {
        "out": 0,
        "living_room": 1,
        "kitchen": 2,
        "bathroom": 3,
        "bedroom": 4,
        "guest_room": 5,
    }

    from tplt_gen.rules import update_rules
    update_rules("CaseStudy")

    # Stage 1. Human/Camera Move
    # Stage 2. Environment change
    # Stage 3. Device animation
    model = Simulatable()
    model.simulation_time = 300
    for i in range(count_tplts("rule_templates/CaseStudy")):
        model.rules_tplt.append(
            open(f'rule_templates/CaseStudy/rule{i+1}.tplt', 'r').read())

    model.locations = ["out", "living_room", "kitchen",
                       "bathroom", "guest_room", "bedroom"]
    model.moving_time = [50.0, 100.0, 150.0, 200.0, 250.0]
    model.devices_tplt.append(
        open('device_templates/Door_240.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Fan_210.tplt', 'r').read())
    model.devices_tplt.append(
        open('device_templates/Curtain_260.tplt', 'r').read())
    model.envs_init['temperature'] = 18.0
    model.envs_tplt.append(
        open('env_templates/temperature.tplt', 'r').read())
    model.build()
    model_path = "models/rq3_case_study.xml"
    open(model_path, "w").write(model.full_body)
    simulate(os.path.abspath(model_path),
             os.path.abspath(model_path + ".result"))


# python -m tplt_gen.devices
# python -m tplt_gen.rules && python -m modeling_old
if __name__ == "__main__":
    build_RQ3_case_4()
