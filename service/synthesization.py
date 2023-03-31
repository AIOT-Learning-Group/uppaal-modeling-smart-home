from modeling.composition import compose_system_behavior_model
from service.external import invoke_external_java_service
from fastapi import APIRouter, Request, Body
from typing import Dict

router = APIRouter()


@router.post("/api/submit-tap-rules")
def submit_tap_rules(request: Request, tap_rules: str = Body(...)) -> Dict[str, str]:
    model = compose_system_behavior_model(tap_rules)
    params = ["--operation=parse-full-xml"]
    params.append("--data=" + model.full_body)
    request.session['system-behavior-model'] = model.full_body
    return invoke_external_java_service(params)


@router.get("/api/filter-interactive-system")
async def filter_interactive_system(request: Request) -> str:
    if not 'system-behavior-model' in request.session.keys():
        return ""
    params = ["--operation=filter-interactive-system"]
    params.append("--data=" + request.session['system-behavior-model'])
    return invoke_external_java_service(params)


@router.get("/api/filter-controller-models")
async def filter_controller_models(request: Request) -> str:
    if not 'system-behavior-model' in request.session.keys():
        return ""
    params = ["--operation=filter-controller-models"]
    params.append("--data=" + request.session['system-behavior-model'])
    return invoke_external_java_service(params)


@router.get("/api/load-time-automaton/{name}")
async def load_time_automaton(request: Request, name: str) -> str:
    if not 'system-behavior-model' in request.session.keys():
        return ""
    params = ["--operation=load-time-automaton", f"--name={name}"]
    params.append("--data=" + request.session['system-behavior-model'])
    return invoke_external_java_service(params)
