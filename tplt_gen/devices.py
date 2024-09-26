import os


def build_two_state_device_with_impacts(name: str = "Device", offset=200, impact_env=None, impact_rate=0, onoff_to_openclose=False):
    positive, negative = "", ""
    if impact_env != None:
        if type(impact_env) is list:
            assert len(impact_env) == len(impact_rate)
            for i in range(len(impact_env)):
                cur_impact_env = impact_env[i]
                cur_impact_rate = impact_rate[i]
                cur_abs_rate = abs(cur_impact_rate)
                if cur_impact_rate > 0:
                    positive += f",{cur_impact_env}={cur_impact_env}+{cur_abs_rate}"
                    negative += f",{cur_impact_env}={cur_impact_env}-{cur_abs_rate}"
                else:
                    positive += f",{cur_impact_env}={cur_impact_env}-{cur_abs_rate}"
                    negative += f",{cur_impact_env}={cur_impact_env}+{cur_abs_rate}"
            pass
        else:
            abs_rate = abs(impact_rate)
            if impact_rate > 0:
                positive = f",{impact_env}={impact_env}+{abs_rate}"
                negative = f",{impact_env}={impact_env}-{abs_rate}"
            else:
                positive = f",{impact_env}={impact_env}-{abs_rate}"
                negative = f",{impact_env}={impact_env}+{abs_rate}"
    tplt = f"""<template>
\t<name>{name}</name>
\t<parameter>int i</parameter>
\t<declaration>//controlled_device</declaration>
\t<location id="id{str(offset)}" x="0" y="25">
\t\t<name x="17" y="16">{name.lower()}on</name>
\t</location>
\t<location id="id{str(offset+1)}" x="0" y="119">
\t\t<name x="-68" y="110">{name.lower()}off</name>
\t</location>
\t<init ref="id{str(offset+1)}"/>
\t<transition>
\t\t<source ref="id{str(offset+1)}"/>
\t\t<target ref="id{str(offset)}"/>
\t\t<label kind="synchronisation" x="-9" y="42">turn_on_{name.lower()}[i]?</label>
\t\t<label kind="assignment" x="17" y="59">{name.lower()}[i]=1{positive}</label>
\t\t<nail x="51" y="76"/>
\t</transition>
\t<transition>
\t\t<source ref="id{str(offset)}"/>
\t\t<target ref="id{str(offset+1)}"/>
\t\t<label kind="synchronisation" x="-85" y="76">turn_off_{name.lower()}[i]?</label>
\t\t<label kind="assignment" x="-85" y="59">{name.lower()}[i]=0{negative}</label>
\t\t<nail x="-51" y="68"/>
\t</transition>
</template>
"""
    global declarations
    decl = ""
    decl += f"int {name.lower()}[1];\n"
    decl += f"urgent broadcast chan turn_on_{name.lower()}[1];\n"
    decl += f"urgent broadcast chan turn_off_{name.lower()}[1];\n"
    if onoff_to_openclose:
        tplt = tplt.replace("turn_on_", "open_").replace("turn_off_", "close_").replace(
            "on</name>", "open</name>").replace("off</name>", "closed</name>")
        decl = decl.replace("turn_on_", "open_").replace("turn_off_", "close_")
    declarations += decl
    return tplt


def build_device_airconditioner(offset=300, impact_rate=0.02):
    global declarations
    declarations += "int airconditioner[1];\n"
    declarations += "urgent broadcast chan turn_airconditioner_off[1];\n"
    declarations += "urgent broadcast chan turn_airconditioner_cool[1];\n"
    declarations += "urgent broadcast chan turn_airconditioner_heat[1];\n"
    return f"""<template>
\t<name>AirConditioner</name>
\t<parameter>int i</parameter>
\t<location id="id{offset}" x="-17" y="25">
\t\t<name x="-17" y="-25">acoff</name>
\t</location>
\t<location id="id{offset+1}" x="-212" y="136">
\t\t<name x="-221" y="144">cool</name>
\t</location>
\t<location id="id{offset+2}" x="195" y="136">
\t\t<name x="178" y="144">heat</name>
\t</location>
\t<init ref="id{offset}"/>
\t<transition>
\t\t<source ref="id{offset}"/>
\t\t<target ref="id{offset+2}"/>
\t\t<label kind="synchronisation" x="85" y="-17">turn_airconditioner_heat[i]?</label>
\t\t<label kind="assignment" x="0" y="25">airconditioner[i]=2,dtemperature=dtemperature+{impact_rate}</label>
\t\t<nail x="195" y="25"/>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+2}"/>
\t\t<target ref="id{offset+1}"/>
\t\t<label kind="synchronisation" x="-59" y="170">turn_airconditioner_cool[i]?</label>
\t\t<label kind="assignment" x="-102" y="187">airconditioner[i]=1,dtemperature=dtemperature-{impact_rate*2}</label>
\t\t<nail x="-17" y="204"/>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+1}"/>
\t\t<target ref="id{offset}"/>
\t\t<label kind="synchronisation" x="-187" y="8">turn_airconditioner_off[i]?</label>
\t\t<label kind="assignment" x="-221" y="25">airconditioner[i]=0,dtemperature=dtemperature+{impact_rate}</label>
\t\t<nail x="-212" y="25"/>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+2}"/>
\t\t<target ref="id{offset}"/>
\t\t<label kind="synchronisation" x="42" y="68">turn_airconditioner_off[i]?</label>
\t\t<label kind="assignment" x="0" y="85">airconditioner[i]=0,dtemperature=dtemperature-{impact_rate}</label>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+1}"/>
\t\t<target ref="id{offset+2}"/>
\t\t<label kind="synchronisation" x="-68" y="119">turn_airconditioner_heat[i]?</label>
\t\t<label kind="assignment" x="-102" y="136">airconditioner[i]=2,dtemperature=dtemperature+{impact_rate*2}</label>
\t</transition>
\t<transition>
\t\t<source ref="id{offset}"/>
\t\t<target ref="id{offset+1}"/>
\t\t<label kind="synchronisation" x="-170" y="68">turn_airconditioner_cool[i]?</label>
\t\t<label kind="assignment" x="-212" y="85">airconditioner[i]=1,dtemperature=dtemperature-{impact_rate}</label>
\t</transition>
</template>"""


def build_sms(offset=300):
    global declarations
    declarations += "int received_msgs=0;\n"
    declarations += "urgent broadcast chan send_msg;\n"
    return f"""<template>
\t<name x="5" y="5">SMS</name>
\t<declaration>// Place local declarations here.</declaration>
\t<location id="id{offset}" x="-170" y="-51">
\t</location>
\t<init ref="id{offset}"/>
\t<transition>
\t\t<source ref="id{offset}"/>
\t\t<target ref="id{offset}"/>
\t\t<label kind="synchronisation" x="-110" y="-68">send_msg?</label>
\t\t<label kind="assignment" x="-110" y="-51">received_msgs += 1</label>
\t\t<nail x="-119" y="-17"/>
\t\t<nail x="-119" y="-76"/>
\t</transition>
</template>"""


def build_rain(offset=400):
    global declarations
    declarations += "int rain=0;\n"
    declarations += "urgent broadcast chan startRain;\n"
    declarations += "urgent broadcast chan stopRain;\n"
    return f"""\t<template>
\t<name x="5" y="5">EnvironmentRain</name>
\t<declaration>// Place local declarations here.
clock t;</declaration>
\t<location id="id{offset}" x="-200" y="-20">
\t\t<name>notRain</name>
\t\t<label kind="exponentialrate" x="-205" y="17">0.01</label>
\t</location>
\t<location id="id{offset+1}" x="0" y="-20">
\t\t<name>Rain</name>
\t\t<label kind="exponentialrate" x="7" y="17">0.026</label>
\t</location>
\t<location id="id{offset+2}" x="-100" y="-50">
\t\t<urgent/>
\t</location>
\t<location id="id{offset+3}" x="-100" y="10">
\t</location>
\t<init ref="id{offset}"/>
\t<transition>
\t\t<source ref="id{offset+3}"/>
\t\t<target ref="id{offset}"/>
\t\t<label kind="synchronisation">stopRain!</label>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+2}"/>
\t\t<target ref="id{offset+1}"/>
\t\t<label kind="synchronisation">startRain!</label>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+1}"/>
\t\t<target ref="id{offset+3}"/>
\t\t<label kind="guard">t&gt;30</label>
\t\t<label kind="assignment">rain=0,t=0</label>
\t</transition>
\t<transition>
\t\t<source ref="id{offset}"/>
\t\t<target ref="id{offset+2}"/>
\t\t<label kind="guard">t&gt;30</label>
\t\t<label kind="assignment">rain=1,t=0</label>
\t</transition>
\t</template>"""


declarations = ""


def build_all():
    if not os.path.exists("device_templates"):
        os.mkdir("device_templates")
    global declarations
    declarations = ""
    open("device_templates/Fan_210.tplt",
         "w").write(build_two_state_device_with_impacts("Fan", 210, "dtemperature", -0.02))
    open("device_templates/AirPurifier_220.tplt",
         "w").write(build_two_state_device_with_impacts("AirPurifier", 220, "dpm_2_5", -0.8))  # PM_2_5：50-250
    open("device_templates/AirConditioner_230.tplt",
         "w").write(build_device_airconditioner(230, 0.05))
    open("device_templates/Door_240.tplt",
         "w").write(build_two_state_device_with_impacts("Door", 240, onoff_to_openclose=True))
    open("device_templates/Light_250.tplt",
         "w").write(build_two_state_device_with_impacts("Light", 250))
    open("device_templates/Curtain_260.tplt",
         "w").write(build_two_state_device_with_impacts("Curtain", 260, onoff_to_openclose=True))
    open("device_templates/Camera_270.tplt",
         "w").write(build_two_state_device_with_impacts("Camera", 270))
    open("device_templates/Humidifier_280.tplt",
         "w").write(build_two_state_device_with_impacts("Humidifier", 280, ["dhumidity", "dpm_2_5"], [+0.1, +0.6]))  # PM_2_5：50-250
    open("device_templates/Window_290.tplt",
         "w").write(build_two_state_device_with_impacts("Window", 290, onoff_to_openclose=True))
    open("device_templates/SMS_300.tplt", "w").write(build_sms(300))
    open("device_templates/Rain_310.tplt", "w").write(build_rain(310))
    open("device_templates/decl", "w").write(declarations)


if __name__ == "__main__":
    build_all()
