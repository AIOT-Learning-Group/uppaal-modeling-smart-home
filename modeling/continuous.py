import math
from scipy import stats  # type: ignore
import numpy as np
from typing import List
from .common import Composition, DataPoints


def build_continuous_template(points: DataPoints, k: int = 1, template_name: str = "Function",
                              clock_name: str = "x", var_name: str = "y", offset: int = 1000) -> Composition:
    x: List[float] = [p[0] for p in points]
    y: List[float] = [p[1] for p in points]
    decl = f"clock {var_name.lower()}; clock d{var_name.lower()};\n"
    sys = f",{template_name}"
    var = f",{var_name.lower()}"
    derivative_name = "d" + var_name.lower()
    template = ""
    template += "\t<template>\n"
    template += f"\t\t<name x=\"5\" y=\"5\">{template_name}</name>\n"
    template += "\t\t<declaration>// Place local declarations here.</declaration>\n"

    template += f"\t\t<location id=\"id{offset}\" x=\"0\" y=\"0\">\n"
    template += f"\t\t\t<label kind=\"invariant\" x=\"0\" y=\"0\">{clock_name} &lt;= 0 &amp;&amp; {var_name}'==0</label>\n"
    template += "\t\t</location>\n"
    if k == 0:
        for i in range(1, len(x)):
            template += f"\t\t<location id=\"id{str(i+offset)}\" x=\"{i*50}\" y=\"0\">\n"
            template += f"\t\t\t<label kind=\"invariant\">{clock_name} &lt;= {x[i]} &amp;&amp; {var_name}'==0</label>\n"
            template += "\t\t</location>\n"
    elif k == 1:
        for i in range(1, len(x)):
            if x[i-1] == x[i]:
                slope = 0
                continue
            else:
                slope, _ = np.polyfit((x[i-1], x[i]), (y[i-1], y[i]), 1)
            template += f"\t\t<location id=\"id{str(i+offset)}\" x=\"{i*50}\" y=\"0\">\n"
            template += f"\t\t\t<label kind=\"invariant\">{clock_name} &lt;= {x[i]} &amp;&amp; {var_name}'=={str(slope)}+{derivative_name}</label>\n"
            template += "\t\t</location>\n"

    template += f"\t\t<location id=\"id{len(x)+offset}\" x=\"{len(x)*50}\" y=\"0\">\n"
    template += f"\t\t\t<label kind=\"invariant\">{var_name}'=={derivative_name}</label>\n"
    template += "\t\t</location>\n"
    template += f"\t\t<init ref=\"id{offset}\"/>\n"

    for i in range(0, len(x)):
        template += "\t\t<transition>\n"
        template += f"\t\t\t<source ref=\"id{str(i+offset)}\"/>\n"
        template += f"\t\t\t<target ref=\"id{str(i+1+offset)}\"/>\n"
        template += f"\t\t\t<label kind=\"guard\">{clock_name} &gt;= {x[i]}</label>\n"
        template += "\t\t</transition>\n"
    template += "\t</template>\n"
    return template, decl, "", sys, var, len(points) + 10


def xy_to_points(x: List[float], y: List[float]) -> DataPoints:
    points: DataPoints = []
    for item in np.column_stack((x, y)):
        _x: float = item[0]
        _y: float = item[1]
        points.append((_x, _y))
    return points


def curve_normal_dist(num: int, init_value: float, height: float) -> DataPoints:
    mu = 0
    variance = 1
    sigma = math.sqrt(variance)
    x = np.linspace(mu - 3 * sigma, mu + 3*sigma, num)
    y = stats.norm.pdf(x, mu, sigma)
    xx: List[float] = list((x + 3) * 4)
    yy: List[float] = list(y / 0.4 * height + init_value)
    return xy_to_points(xx, yy)


def remap(points: DataPoints, new_range: int) -> DataPoints:
    x = np.array([p[0] for p in points])
    yy = [p[1] for p in points]
    ori_range = np.max(x) - np.min(x)
    x = x / ori_range * new_range
    xx: List[float] = [i for i in x]
    return xy_to_points(xx, yy)
