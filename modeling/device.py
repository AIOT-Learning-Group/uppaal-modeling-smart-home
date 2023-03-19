from typing import Union, List
from modeling.common import PartialComposition, ComposableTemplate


def build_two_state_device_with_impacts(name: str = "Device", offset: int = 200, impact_env: Union[None, str, List[str]] = None, impact_rate: Union[float, List[float]] = 0, onoff_to_openclose: bool = False) -> PartialComposition:
    positive, negative = "", ""
    if impact_env != None:
        if type(impact_env) is list and type(impact_rate) is list:
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
        elif type(impact_rate) is float:
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
    decl = ""
    decl += f"int {name.lower()}[{{number}}];\n"
    decl += f"urgent broadcast chan turn_on_{name.lower()}[{{number}}];\n"
    decl += f"urgent broadcast chan turn_off_{name.lower()}[{{number}}];\n"
    if onoff_to_openclose:
        tplt = tplt.replace("turn_on_", "open_").replace("turn_off_", "close_").replace(
            "on</name>", "open</name>").replace("off</name>", "closed</name>")
        decl = decl.replace("turn_on_", "open_").replace("turn_off_", "close_")
    return name, tplt, decl


Fan = ComposableTemplate(lambda x: build_two_state_device_with_impacts(
    "Fan", x, "dtemperature", -0.02), 2)
AirPurifier = ComposableTemplate(lambda x: build_two_state_device_with_impacts(
    "AirPurifier", x, "dpm_2_5", -0.8), 2)
Door = ComposableTemplate(lambda x: build_two_state_device_with_impacts(
    "Door", x, onoff_to_openclose=True), 2)
Light = ComposableTemplate(lambda x: build_two_state_device_with_impacts(
    "Light", x), 2)
Curtain = ComposableTemplate(lambda x: build_two_state_device_with_impacts(
    "Curtain", x, onoff_to_openclose=True), 2)
Camera = ComposableTemplate(lambda x: build_two_state_device_with_impacts(
    "Camera", x), 2)
Humidifier = ComposableTemplate(lambda x: build_two_state_device_with_impacts(
    "Humidifier", x, ["dhumidity", "dpm_2_5"], [+0.1, +0.6]), 2)
Window = ComposableTemplate(lambda x: build_two_state_device_with_impacts(
    "Window", x, onoff_to_openclose=True), 2)


def build_device_air_conditioner(offset: int = 300, impact_rate: float = 0.02) -> PartialComposition:
    name = "AirConditioner"
    decl = f"int {name.lower()}[{{number}}];\n"
    decl += "urgent broadcast chan turn_ac_off[{number}];\n"
    decl += "urgent broadcast chan turn_ac_cool[{number}];\n"
    decl += "urgent broadcast chan turn_ac_heat[{number}];\n"
    return name, f"""<template>
\t<name>{name}</name>
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
\t\t<label kind="synchronisation" x="85" y="-17">turn_ac_heat[i]?</label>
\t\t<label kind="assignment" x="0" y="25">airconditioner[i]=2,dtemperature=dtemperature+{impact_rate}</label>
\t\t<nail x="195" y="25"/>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+2}"/>
\t\t<target ref="id{offset+1}"/>
\t\t<label kind="synchronisation" x="-59" y="170">turn_ac_cool[i]?</label>
\t\t<label kind="assignment" x="-102" y="187">airconditioner[i]=1,dtemperature=dtemperature-{impact_rate*2}</label>
\t\t<nail x="-17" y="204"/>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+1}"/>
\t\t<target ref="id{offset}"/>
\t\t<label kind="synchronisation" x="-187" y="8">turn_ac_off[i]?</label>
\t\t<label kind="assignment" x="-221" y="25">airconditioner[i]=0,dtemperature=dtemperature+{impact_rate}</label>
\t\t<nail x="-212" y="25"/>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+2}"/>
\t\t<target ref="id{offset}"/>
\t\t<label kind="synchronisation" x="42" y="68">turn_ac_off[i]?</label>
\t\t<label kind="assignment" x="0" y="85">airconditioner[i]=0,dtemperature=dtemperature-{impact_rate}</label>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+1}"/>
\t\t<target ref="id{offset+2}"/>
\t\t<label kind="synchronisation" x="-68" y="119">turn_ac_heat[i]?</label>
\t\t<label kind="assignment" x="-102" y="136">airconditioner[i]=2,dtemperature=dtemperature+{impact_rate*2}</label>
\t</transition>
\t<transition>
\t\t<source ref="id{offset}"/>
\t\t<target ref="id{offset+1}"/>
\t\t<label kind="synchronisation" x="-170" y="68">turn_ac_cool[i]?</label>
\t\t<label kind="assignment" x="-212" y="85">airconditioner[i]=1,dtemperature=dtemperature-{impact_rate}</label>
\t</transition>
</template>""", decl


AirConditioner = ComposableTemplate(
    lambda x: build_device_air_conditioner(x, 0.05), 3)


def build_sms(offset: int = 300) -> PartialComposition:
    name = "SMS"
    decl = f"int {name.lower()}=0;\n"
    decl += "urgent broadcast chan send_msg;\n"
    return name, f"""<template>
\t<name x="5" y="5">SMS</name>
\t<declaration>// Place local declarations here.</declaration>
\t<location id="id{offset}" x="-170" y="-51">
\t</location>
\t<init ref="id{offset}"/>
\t<transition>
\t\t<source ref="id{offset}"/>
\t\t<target ref="id{offset}"/>
\t\t<label kind="synchronisation" x="-110" y="-68">send_msg?</label>
\t\t<label kind="assignment" x="-110" y="-51">{name.lower()} += 1</label>
\t\t<nail x="-119" y="-17"/>
\t\t<nail x="-119" y="-76"/>
\t</transition>
</template>""", decl


SMS = ComposableTemplate(
    lambda x: build_sms(x), 1)
