import os
from config import POINTS_NUMBER
from config import UPPAAL_PATH
from loguru import logger
import subprocess
import tempfile
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from typing import Tuple, List, Callable, Dict, Union, Optional
from typing_extensions import TypedDict, TypeAlias
from modeling.common import DataPoints, DataPointsGenerator, TemplateGenerator
from modeling.composition import Simulation
from modeling.continuous import build_continuous_template, curve_constant, curve_normal_dist, remap
from modeling.human import HumanModelForSmartHome
from service.utils import handle_assertion, save_to_archives

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
#             {"name": "Cosine curve", "parameters": [
#                 "Initial value", "Range", "Highest", "Lowest"]},
#             {"name": "Collected data for RQ2", "parameters": ["Initial value"]}
#         ]
#     },
# ]

ParserInput = Tuple[str, Dict[str, str]]
ParserOutput: TypeAlias = Optional[TemplateGenerator]

CMSParser = Callable[[ParserInput], ParserOutput]
CMSGenerator = Callable[..., List[ModelInstanceSpecification]]


def get_human_model_specification() -> List[ModelInstanceSpecification]:
    # TODO: map animation specification to patterns
    patterns = [
        # ["out", "living_room", "kitchen", "bathroom", "bedroom", "guest_room"],
        # ["out", "living_room", "bathroom", "bedroom"],
        # ["out", "living_room", "bedroom", "living_room", "out"]
        ["out", "doorway", "home"],
        ["out", "living_room", "kitchen", "bedroom"],
        ["out", "living_room", "kitchen", "bathroom", "guest_room", "bedroom"],
    ]
    params = [[f"t{i+1}" for i in range(len(pat) - 1)] for pat in patterns]
    specs: List[ModelInstanceSpecification] = []
    for i in range(len(patterns)):
        specs.append({"name": "->".join(patterns[i]), "parameters": params[i]})
    return specs


def parse_human_model_specification(input: ParserInput) -> ParserOutput:
    inst_name, params = input
    places = inst_name.split("->")
    params.pop(SIM_TIME_PARAM_NAME)
    assert len(places) == len(params.keys()) + \
        1, f"bad params number: {len(params.keys())} expected"
    params_value = [float(params[f"t{i+1}"]) for i in range(len(places) - 1)]
    return lambda x: HumanModelForSmartHome.compose(x, places, params_value)


const_params = ["Initial Value"]
norm_params = ["Initial Value", "Height"]
# cos_params = ["A", "B", "C", "D"]


def const_gen(num: int, params: Dict[str, str]) -> DataPoints:
    for param_name in const_params:
        assert param_name in params.keys(), "lack of param: " + param_name
    return curve_constant(num, float(params[const_params[0]]))


def norm_gen(num: int, params: Dict[str, str]) -> DataPoints:
    for param_name in norm_params:
        assert param_name in params.keys(), "lack of param: " + param_name
    return curve_normal_dist(num, float(params[norm_params[0]]), float(params[norm_params[1]]))


Curve = Tuple[str, List[str], DataPointsGenerator]
ConstantCurve: Curve = ("Constant", const_params, const_gen)
NormalDistributionCurve: Curve = ("Gaussian Curve", norm_params, norm_gen) # TODO: Revert

temperature_models: List[Curve] = [ConstantCurve, NormalDistributionCurve]
humidity_models: List[Curve] = [ConstantCurve, NormalDistributionCurve]
pm25_models: List[Curve] = [ConstantCurve, NormalDistributionCurve]
# temperature_models: List[Curve] = [("Constant Temperature", const_params, const_gen), ("Cosine Temperature", cos_params, norm_gen)] # todo: FIX
# humidity_models: List[Curve] = [("Constant Humidity", const_params, const_gen), ("Gaussian Humidity", norm_params, norm_gen)]
# carbonmonoxide_models: List[Curve] = [("Indoor Carbon Monoxide In Shanghai", const_params, const_gen)]
# brightness_models: List[Curve] = [("Indoor Brightness In Shanghai", const_params, const_gen)]

def get_temperature_model_specification() -> List[ModelInstanceSpecification]:
    return [{"name": c[0], "parameters": c[1]} for c in temperature_models]


def parse_temperature_model_specification(input: ParserInput) -> ParserOutput:
    node_num = POINTS_NUMBER
    inst_name, params = input
    for name, _, generator in temperature_models:
        if inst_name == name:
            sim_time = int(params[SIM_TIME_PARAM_NAME])
            dpoints = generator(node_num, params)
            return lambda x: build_continuous_template(remap(dpoints, sim_time), template_name="EnvironmentTemperature",
                                                       clock_name="time", var_name="temperature", offset=x)
    return None


def get_humidity_model_specification() -> List[ModelInstanceSpecification]:
    return [{"name": c[0], "parameters": c[1]} for c in humidity_models]


def parse_humidity_model_specification(input: ParserInput) -> ParserOutput:
    node_num = POINTS_NUMBER
    inst_name, params = input
    for name, _, generator in humidity_models:
        if inst_name == name:
            sim_time = int(params[SIM_TIME_PARAM_NAME])
            dpoints = generator(node_num, params)
            return lambda x: build_continuous_template(remap(dpoints, sim_time), template_name="EnvironmentHumidity",
                                                       clock_name="time", var_name="humidity", offset=x)
    return None



def get_pm25_model_specification() -> List[ModelInstanceSpecification]:
    return [{"name": c[0], "parameters": c[1]} for c in pm25_models]


def parse_pm25_model_specification(input: ParserInput) -> ParserOutput:
    node_num = POINTS_NUMBER
    inst_name, params = input
    for name, _, generator in humidity_models:
        if inst_name == name:
            sim_time = int(params[SIM_TIME_PARAM_NAME])
            dpoints = generator(node_num, params)
            return lambda x: build_continuous_template(remap(dpoints, sim_time), template_name="EnvironmentPM25",
                                                       clock_name="time", var_name="pm25", offset=x)
    return None

# def get_brightness_model_specification() -> List[ModelInstanceSpecification]:
#     return [{"name": c[0], "parameters": c[1]} for c in brightness_models]

# def parse_brightness_model_specification(input: ParserInput) -> ParserOutput:
#     return None

context_models: Dict[str, Tuple[CMSGenerator, CMSParser]] = {}
context_models["Human Activities"] = (
    get_human_model_specification, parse_human_model_specification)
context_models["Temperature"] = (
    get_temperature_model_specification, parse_temperature_model_specification
)
context_models["Humidity"] = (
    get_humidity_model_specification, parse_humidity_model_specification
)
context_models["PM25"] = (
    get_pm25_model_specification, parse_pm25_model_specification
)
# context_models["CarbonMonoxide"] = (
#     get_carbonmonoxide_model_specification, parse_carbonmonoxide_model_specification
# )
# context_models["Brightness"] = (
#     get_brightness_model_specification, parse_brightness_model_specification
# )


@router.get("/api/fetch-context-model")
async def fetch_context_model() -> List[ContextModelSpecification]:
    return [{"name": name, "models": gen()} for name, (gen, _) in context_models.items()]


@router.post("/api/submit-simulation-params", response_class=PlainTextResponse)
async def submit_simulation_params(request: Request) -> Union[str, Dict[str, str]]:
    try:
        result = await parse_simulation_params(await request.json())
        return result
    except AssertionError as err:
        return {"error": handle_assertion(err)}


def run(sim: Simulation) -> str:
    model_path = tempfile.NamedTemporaryFile().name + ".xml"
    open(model_path, "w").write(sim.full_body)
    save_to_archives("rules", os.path.basename(
        model_path).replace(".xml", "_rules.txt"), sim.raw_rules)
    save_to_archives("models", os.path.basename(model_path), sim.full_body)
    result_path = model_path + ".result"
    if os.name == 'nt':
        cmd = f"cmd /c verifyta -O std {model_path} > {result_path}".split(" ")
        result = subprocess.run(
            cmd, cwd=UPPAAL_PATH, stdout=subprocess.PIPE, text=True)
    else:
        result = subprocess.run(["./verifyta", "-O", "std", model_path],
                                cwd=UPPAAL_PATH, capture_output=True, text=True)
        open(result_path, "w").write(str(result.stdout))
    logger.info(
        f'subproc args:{" ".join(result.args)}, retcode: {str(result.returncode)}')
    result_str = open(result_path, "r").read()
    save_to_archives("results", os.path.basename(result_path), result_str)
    return result_str


SIM_TIME_PARAM_NAME = "Simulation Time"


async def parse_simulation_params(raw_params: Tuple[List[Dict[str, str]], List[Dict[str, str]], str, str]) -> str:
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
        params[SIM_TIME_PARAM_NAME] = simulation_time
        _, parser = context_models[model_name]
        tplt_gen = parser((inst_name, params))
        if tplt_gen is not None:
            simulation.add_tplt_gen(tplt_gen)
    simulation.compose(int(simulation_time))
    return run(simulation)


if __name__ == "__main__":
    simulation = Simulation()
    simulation.load_tap_rules("")
    sim_time = 300
    points_number = 5
    dpoints = curve_normal_dist(points_number, 24.0, 8.0)
    simulation.add_tplt_gen(lambda x: build_continuous_template(
        remap(dpoints, sim_time), template_name="EnvironmentTemperature",
        clock_name="time", var_name="temperature", offset=x))
    simulation.compose(int(sim_time))
    open("test_model.xml", "w").write(simulation.full_body)
