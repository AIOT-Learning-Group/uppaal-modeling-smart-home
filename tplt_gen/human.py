
locations_ids = {
    "out": 0,
    "doorway": 1,
    "home": 2,
}


def build_human(locations, offset=100):
    global locations_ids
    occurrence = {}
    template = ""
    template += "<template>\n"
    template += "\t<name>Human</name>\n"
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
        location_id = locations_ids[locations[i]]
        template += f'\t<transition>\n'
        template += f'\t\t<source ref="id{str(offset+i)}"/>\n'
        template += f'\t\t<target ref="id{str(offset+i+1)}"/>\n'
        if i > 0:
            template += f'\t\t<label kind="guard">time&gt;=t{str(i-1)}</label>\n'
        template += f'\t\t<label kind="assignment">position={location_id}</label>\n'
        template += f'\t</transition>\n'
    template += "</template>\n"
    return template
