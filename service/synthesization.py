from modeling.composition import compose_system_behavior_model
from service.utils import handle_assertion
from service.external import invoke_external_java_service
from fastapi import APIRouter, Body
from typing import Dict

router = APIRouter()


@router.post("/api/submit-tap-rules")
def submit_tap_rules(tap_rules: str = Body(...)) -> Dict[str, str]:
    try:
        model = compose_system_behavior_model(tap_rules)
        params = ["--operation=parse-full-xml"]
        params.append("--data=" + model.full_body)
        return {"result": invoke_external_java_service(params), "model": model.full_body, "tap_rules": tap_rules}
    except AssertionError as err:
        return {"error": handle_assertion(err)}


@router.post("/api/filter-interactive-system")
async def filter_interactive_system(model: str = Body(...)) -> str:
    params = ["--operation=filter-interactive-system"]
    params.append("--data=" + model)
    result = invoke_external_java_service(params)
    print(model)
    print(result)
    return result


@router.post("/api/filter-controller-models")
async def filter_controller_models(model: str = Body(...)) -> str:
    params = ["--operation=filter-controller-models"]
    params.append("--data=" + model)
    return invoke_external_java_service(params)


@router.post("/api/load-time-automaton/{name}")
async def load_time_automaton(name: str, model: str = Body(...)) -> str:
    params = ["--operation=load-time-automaton", f"--name={name}"]
    params.append("--data=" + model)
    return invoke_external_java_service(params)
