from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from typing import Tuple, List, Callable, Dict, Union, Optional
from typing_extensions import TypedDict, TypeAlias
from modeling.common import DataPoints, DataPointsGenerator, TemplateGenerator
from modeling.composition import Simulation
from modeling.continuous import build_continuous_template, curve_normal_dist
from modeling.human import HumanModelForSmartHome
from service.utils import handle_assertion

router = APIRouter()


class ModelInstanceSpecification(TypedDict):
    name: str
    parameters: List[str]


class ContextModelSpecification(TypedDict):
    name: str
    models: List[ModelInstanceSpecification]


# context_model: List[ContextModelSpecification] = [
#     {
#         "name": "Environment Temperature",
#         "models":
#         [
#             {"name": "Constant value", "parameters": ["Initial value"]},
#             {"name": "Gaussian curve", "parameters": [
#                 "Initial value", "Range"]},
#             {"name": "Cosine curve", "parameters": [
#                 "Initial value", "Range", "Highest", "Lowest"]},
#             {"name": "Collected data for RQ2", "parameters": ["Initial value"]}
#         ]
#     },
#     {
#         "name": "Environment Humidity",
#         "models":
#         [
#             {"name": "Constant value", "parameters": ["Initial value"]}
#         ]
#     }
# ]

ParserInput = Tuple[str, Dict[str, str]]
ParserOutput: TypeAlias = Optional[TemplateGenerator]

CMSParser = Callable[[ParserInput], ParserOutput]
CMSGenerator = Callable[..., List[ModelInstanceSpecification]]


def get_human_model_specification() -> List[ModelInstanceSpecification]:
    # TODO: map animation specification to patterns
    patterns = [
        ["out", "living_room", "kitchen", "bathroom", "bedroom", "guest_room"],
        ["out", "living_room", "bedroom"],
        ["out", "living_room", "bedroom", "living_room", "out"]
    ]
    params = [[f"t{i+1}" for i in range(len(pat) - 1)] for pat in patterns]
    specs: List[ModelInstanceSpecification] = []
    for i in range(len(patterns)):
        specs.append({"name": "->".join(patterns[i]), "parameters": params[i]})
    return specs


def parse_human_model_specification(input: ParserInput) -> ParserOutput:
    inst_name, params = input
    places = inst_name.split("->")
    assert len(places) == len(params.keys()) + \
        1, f"bad params number: {len(params.keys())} expected"
    params_value = [float(params[f"t{i+1}"]) for i in range(len(places) - 1)]
    return lambda x: HumanModelForSmartHome.compose(x, places, params_value)


# [Name, Parameter Names, Generator]
Curve = Tuple[str, List[str], DataPointsGenerator]

norm_params = ["Initial Value", "Height"]


def norm_gen(num: int, params: Dict[str, str]) -> DataPoints:
    for param_name in norm_params:
        assert param_name in params.keys(), "lack of param: " + param_name
    return curve_normal_dist(num, float(params[norm_params[0]]), float(params[norm_params[1]]))


NormalDistributionCurve: Curve = ("Gaussian Curve", norm_params, norm_gen)


def get_temperature_model_specification() -> List[ModelInstanceSpecification]:
    return [{"name": c[0], "parameters": c[1]} for c in [NormalDistributionCurve]]


def parse_temperature_model_specification(input: ParserInput) -> ParserOutput:
    print("b")
    node_num = 500
    inst_name, params = input
    for name, _, generator in [NormalDistributionCurve]:
        if inst_name == name:
            dpoints = generator(node_num, params)
            return lambda x: build_continuous_template(dpoints, template_name="EnvironmentTemperature", clock_name="time", var_name="temperature", offset=x)
    return None


context_models: Dict[str, Tuple[CMSGenerator, CMSParser]] = {}
context_models["Human Activities"] = (
    get_human_model_specification, parse_human_model_specification)
context_models["Environment Temperature"] = (
    get_temperature_model_specification, parse_temperature_model_specification
)


@router.get("/api/fetch-context-model")
async def fetch_context_model() -> List[ContextModelSpecification]:
    return [{"name": name, "models": gen()} for name, (gen, _) in context_models.items()]


@router.post("/api/submit-simulation-params", response_class=PlainTextResponse)
async def submit_simulation_params(request: Request) -> Union[str, Dict[str, str]]:
    try:
        await parse_simulation_params(await request.json())
        return mocking_simulation_result
    except AssertionError as err:
        return {"error": handle_assertion(err)}


async def parse_simulation_params(raw_params: Tuple[List[Dict[str, str]], List[Dict[str, str]], str, str]) -> None:
    input_values, selected_models, simulation_time, tap_rules = raw_params
    simulation = Simulation()
    simulation.load_tap_rules(tap_rules)
    for selected_model in selected_models:
        params: Dict[str, str] = {}
        assert len(selected_model.keys()
                   ) == 1, f"bad data format: {selected_model}"
        model_name, inst_name = list(selected_model.items())[0]
        assert model_name in context_models.keys(
        ), f"bad model name: {model_name}"
        param_prefix = f"{model_name}/{inst_name}/"
        for input_value in input_values:
            full_param_name, param_var = list(input_value.items())[0]
            if (full_param_name.startswith(param_prefix)):
                param_name = full_param_name.replace(param_prefix, "")
                params[param_name] = param_var

        _, parser = context_models[model_name]
        parser((inst_name, params))

mocking_simulation_result = '''temperature:
[0]: (0, 18.54) (0, 18.54) (0.77, 18.54) (0.77, 18.54) (11.44, 21.65) (11.44, 21.65) (12.63, 22) (12.63, 22) (19.74, 21.52) (19.74, 21.52) (20.93, 21.32) (20.93, 21.32) (22.11, 21.08) (22.11, 21.08) (23.30, 21.04) (23.30, 21.04) (31.60, 21.48) (31.60, 21.48) (32.79, 21.52) (32.79, 21.52) (52.94, 22) (52.94, 22) (54.13, 22.02) (54.13, 22.02) (76.66, 22.48) (76.66, 22.48) (77.85, 22.49) (77.85, 22.49) (84.96, 22.04) (84.96, 22.04) (86.15, 21.95) (86.15, 21.95) (90.89, 21.51) (90.89, 21.51) (92.07, 21.44) (92.07, 21.44) (99.19, 21.04) (99.19, 21.04) (100.37, 21.17) (100.37, 21.17) (101.56, 21.49) (101.56, 21.49) (112.23, 21.01) (112.23, 21.01) (113.42, 21.26) (113.42, 21.26) (114.60, 21.45) (114.60, 21.45) (116.98, 21.14) (116.98, 21.14) (118.16, 21.01) (118.16, 21.01) (121.72, 21.47) (121.72, 21.47) (122.90, 21.46) (122.90, 21.46) (133.58, 21.03) (133.58, 21.03) (134.76, 21.17) (134.76, 21.17) (135.95, 21.46) (135.95, 21.46) (137.13, 21.18) (137.13, 21.18) (138.32, 21.06) (138.32, 21.06) (140.69, 21.39) (140.69, 21.39) (141.88, 21.49) (141.88, 21.49) (153.73, 21.04) (153.73, 21.04) (154.92, 21.01) (154.92, 21.01) (158.48, 21.50) (158.48, 21.50) (159.66, 21.40) (159.66, 21.40) (164.41, 21) (164.41, 21) (165.59, 21.55) (165.59, 21.55) (172.71, 21.99) (172.71, 21.99) (173.89, 21.90) (173.89, 21.90) (177.45, 21.54) (177.45, 21.54) (178.64, 21.59) (178.64, 21.59) (182.19, 21.99) (182.19, 21.99) (183.38, 21.96) (183.38, 21.96) (196.42, 21.50) (196.42, 21.50) (197.61, 21.28) (197.61, 21.28) (198.79, 21.03) (198.79, 21.03) (199.98, 20.91) (199.98, 20.91) (203.54, 20.59) (203.54, 20.59) (204.72, 20.50) (204.72, 20.50) (220.14, 20.02) (220.14, 20.02) (221.32, 19.99) (221.32, 19.99) (236.74, 19.51) (236.74, 19.51) (237.92, 19.58) (237.92, 19.58) (241.48, 19.93) (241.48, 19.93) (242.67, 19.98) (242.67, 19.98) (256.90, 19.51) (256.90, 19.51) (258.08, 19.53) (258.08, 19.53) (273.50, 19.98) (273.50, 19.98) (274.68, 19.81) (274.68, 19.81) (275.87, 19.48) (275.87, 19.48) (278.24, 19.05) (278.24, 19.05) (279.43, 18.91) (279.43, 18.91) (282.98, 18.56) (282.98, 18.56) (284.17, 18.62) (284.17, 18.62) (285.36, 18.85) (285.36, 18.85) (286.54, 18.61) (286.54, 18.61) (287.73, 18.60) (287.73, 18.60) (288.91, 18.90) (288.91, 18.90) (290.10, 18.58) (290.10, 18.58) (291.28, 18.37) (291.28, 18.37) (293.66, 18.07) (293.66, 18.07) (294.84, 17.90) (294.84, 17.90) (297.21, 17.50) (297.21, 17.50) (298.40, 17.85) (298.40, 17.85) (299.58, 18.19) (299.58, 18.19) (300.01, 18.19)
fan[0]:
[0]: (0, 0) (0, 0) (110, 0) (110, 0) (110.07, 1) (110.07, 1) (120, 1) (120, 1) (120.07, 0) (120.07, 0) (300.01, 0)
lamp[0]:
[0]: (0, 0) (0, 0) (130, 0) (130, 0) (130.07, 1) (130.07, 1) (150, 1) (150, 1) (150.07, 0) (150.07, 0) (200, 0) (200, 0) (200.07, 1) (200.07, 1) (240, 1) (240, 1) (240.07, 0) (240.07, 0) (300.01, 0)
airpurifier[0]:
[0]: (0, 0) (0, 0) (170, 0) (170, 0) (170.07, 1) (170.07, 1) (240, 1) (240, 1) (240.07, 0) (240.07, 0) (300.01, 0)
position:
[0]: (0, 0) (0, 0) (106.25, 0) (106.25, 0) (106.31, 1) (106.31, 1) (118.75, 1) (118.75, 1) (118.82, 0) (118.82, 0) (121.88, 0) (121.88, 0) (121.94, 2) (121.94, 2) (146.88, 2) (146.88, 2) (146.94, 0) (146.94, 0) (168.75, 0) (168.75, 0) (168.82, 3) (168.82, 3) (193.75, 3) (193.75, 3) (193.82, 2) (193.82, 2) (200, 2) (200, 2) (200.07, 0) (200.07, 0) (206.25, 0) (206.25, 0) (206.32, 1) (206.32, 1) (225, 1) (225, 1) (225.07, 3) (225.07, 3) (231.25, 3) (231.25, 3) (231.32, 0) (231.32, 0) (300.01, 0)
rule1:
[0]: (0, 0) (0, 0) (110, 0) (110, 0) (110.07, 1) (110.07, 1) (120, 1) (120, 1) (120.07, 0) (120.07, 0) (300.01, 0)
rule2:
[0]: (0, 0) (0, 0) (130, 0) (130, 0) (130.07, 1) (130.07, 1) (150, 1) (150, 1) (150.07, 0) (150.07, 0) (200, 0) (200, 0) (200.07, 1) (200.07, 1) (210, 1) (210, 1) (210.07, 0) (210.07, 0) (300.01, 0)
rule3:
[0]: (0, 0) (0, 0) (170, 0) (170, 0) (170.07, 1) (170.07, 1) (200, 1) (200, 1) (200.07, 0) (200.07, 0) (230, 0) (230, 0) (230.07, 1) (230.07, 1) (240, 1) (240, 1) (240.07, 0) (240.07, 0) (300.01, 0)
rule4:
[0]: (0, 0) (0, 0) (10, 0) (10, 0) (10.07, 1) (10.07, 1) (110, 1) (110, 1) (110.07, 0) (110.07, 0) (120, 0) (120, 0) (120.07, 1) (120.07, 1) (130, 1) (130, 1) (130.07, 0) (130.07, 0) (150, 0) (150, 0) (150.07, 1) (150.07, 1) (170, 1) (170, 1) (170.07, 0) (170.07, 0) (240, 0) (240, 0) (240.07, 1) (240.07, 1) (300.01, 1)
rule5:
[0]: (0, 0) (0, 0) (10, 0) (10, 0) (10.07, 1) (10.07, 1) (110, 1) (110, 1) (110.07, 0) (110.07, 0) (120, 0) (120, 0) (120.07, 1) (120.07, 1) (130, 1) (130, 1) (130.07, 0) (130.07, 0) (150, 0) (150, 0) (150.07, 1) (150.07, 1) (170, 1) (170, 1) (170.07, 0) (170.07, 0) (240, 0) (240, 0) (240.07, 1) (240.07, 1) (300.01, 1)
rule6:
[0]: (0, 0) (0, 0) (10, 0) (10, 0) (10.07, 1) (10.07, 1) (110, 1) (110, 1) (110.07, 0) (110.07, 0) (120, 0) (120, 0) (120.07, 1) (120.07, 1) (130, 1) (130, 1) (130.07, 0) (130.07, 0) (150, 0) (150, 0) (150.07, 1) (150.07, 1) (170, 1) (170, 1) (170.07, 0) (170.07, 0) (240, 0) (240, 0) (240.07, 1) (240.07, 1) (300.01, 1)
'''
