import os


def build_two_state_device_with_impacts(name: str = "Device", offset=200, impact_env=None, impact_rate=0):
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
    return f"""<template>
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


def build_device_air_conditioner(offset=300, impact_rate=0.02):
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
\t\t<label kind="synchronisation" x="85" y="-17">turn_ac_heat[i]?</label>
\t\t<label kind="assignment" x="0" y="25">ac[i]=2,dtemperature=dtemperature+{impact_rate}</label>
\t\t<nail x="195" y="25"/>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+2}"/>
\t\t<target ref="id{offset+1}"/>
\t\t<label kind="synchronisation" x="-59" y="170">turn_ac_cool[i]?</label>
\t\t<label kind="assignment" x="-102" y="187">ac[i]=1,dtemperature=dtemperature-{impact_rate*2}</label>
\t\t<nail x="-17" y="204"/>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+1}"/>
\t\t<target ref="id{offset}"/>
\t\t<label kind="synchronisation" x="-187" y="8">turn_ac_off[i]?</label>
\t\t<label kind="assignment" x="-221" y="25">ac[i]=0,dtemperature=dtemperature+{impact_rate}</label>
\t\t<nail x="-212" y="25"/>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+2}"/>
\t\t<target ref="id{offset}"/>
\t\t<label kind="synchronisation" x="42" y="68">turn_ac_off[i]?</label>
\t\t<label kind="assignment" x="0" y="85">ac[i]=0,dtemperature=dtemperature-{impact_rate}</label>
\t</transition>
\t<transition>
\t\t<source ref="id{offset+1}"/>
\t\t<target ref="id{offset+2}"/>
\t\t<label kind="synchronisation" x="-68" y="119">turn_ac_heat[i]?</label>
\t\t<label kind="assignment" x="-102" y="136">ac[i]=2,dtemperature=dtemperature+{impact_rate*2}</label>
\t</transition>
\t<transition>
\t\t<source ref="id{offset}"/>
\t\t<target ref="id{offset+1}"/>
\t\t<label kind="synchronisation" x="-170" y="68">turn_ac_cool[i]?</label>
\t\t<label kind="assignment" x="-212" y="85">ac[i]=1,dtemperature=dtemperature-{impact_rate}</label>
\t</transition>
</template>"""


def build_sms(offset=300):
    return f"""<template>
\t<name x="5" y="5">SMS</name>
\t<declaration>// Place local declarations here.</declaration>
\t<location id="id{offset}" x="-170" y="-51">
\t\t<urgent/>
\t</location>
\t<init ref="id0"/>
\t<transition>
\t\t<source ref="id{offset}"/>
\t\t<target ref="id{offset}"/>
\t\t<label kind="synchronisation" x="-110" y="-68">send_sms?</label>
\t\t<label kind="assignment" x="-110" y="-51">received_msgs += 1</label>
\t\t<nail x="-119" y="-17"/>
\t\t<nail x="-119" y="-76"/>
\t</transition>
</template>"""


def onoff_to_openclose(input: str) -> str:
    return input.replace("turn_on_", "open_").replace("turn_off_", "close_").replace(
        "on</name>", "open</name>").replace("off</name>", "closed</name>")


def build_all():
    if not os.path.exists("device_templates"):
        os.mkdir("device_templates")

    open("device_templates/Fan_210.tplt",
         "w").write(build_two_state_device_with_impacts("Fan", 210, "dtemperature", -0.02))
    open("device_templates/AirPurifier_220.tplt",
         "w").write(build_two_state_device_with_impacts("AirPurifier", 220, "dpm_2_5", -0.1))  # PM_2_5：50-250
    open("device_templates/AirConditioner_230.tplt",
         "w").write(build_device_air_conditioner(230, 0.05))
    open("device_templates/Door_240.tplt",
         "w").write(onoff_to_openclose(build_two_state_device_with_impacts("Door", 240)))
    open("device_templates/Light_250.tplt",
         "w").write(build_two_state_device_with_impacts("Light", 250))
    open("device_templates/Curtain_260.tplt",
         "w").write(build_two_state_device_with_impacts("Curtain", 260))
    open("device_templates/Camera_270.tplt",
         "w").write(onoff_to_openclose(build_two_state_device_with_impacts("Camera", 270)))
    open("device_templates/Humidifier_280.tplt",
         "w").write(build_two_state_device_with_impacts("Humidifier", 280, ["dhumidity", "dpm_2_5"], [+0.1, +1]))  # PM_2_5：50-250
    open("device_templates/Window_290.tplt",
         "w").write(onoff_to_openclose(build_two_state_device_with_impacts("Window", 290)))
    open("device_templates/SMS_300.tplt", "w").write(build_sms(300))


if __name__ == "__main__":
    build_all()
