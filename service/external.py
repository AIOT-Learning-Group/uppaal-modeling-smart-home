from fastapi import APIRouter, Request, Body
import json
from typing import List
import subprocess

DRAWER_PATH = "epg_service_jar/epg-service.jar"


def invoke_external_java_service(executive: str, params: List[str]) -> str:
    prefix = ['java', '-jar', executive]
    result = subprocess.run(prefix + params, stdout=subprocess.PIPE, text=True)
    return result.stdout


router = APIRouter()


@router.post("/api/external/parse-full-xml")
async def parse_full_xml(request: Request, raw_text: str = Body(...)):
    request.session['full-xml'] = raw_text
    params = ["--operation=parse-full-xml"]
    params.append("--data=" + request.session['full-xml'])
    return invoke_external_java_service(DRAWER_PATH, params)


@router.get("/api/external/filter-interactive-system")
async def filter_interactive_system(request: Request):
    if not 'full-xml' in request.session.keys():
        return
    params = ["--operation=filter-interactive-system"]
    params.append("--data=" + request.session['full-xml'])
    return invoke_external_java_service(DRAWER_PATH, params)


@router.get("/api/external/filter-controller-models")
async def filter_controller_models(request: Request):
    if not 'full-xml' in request.session.keys():
        return
    params = ["--operation=filter-controller-models"]
    params.append("--data=" + request.session['full-xml'])
    return invoke_external_java_service(DRAWER_PATH, params)


if __name__ == "__main__":
    prefix = ['java', '-jar', "epg_service_jar/epg-service.jar"]
    params = ["--operation=load-time-automaton", "--name=Rule1"]
    params.append("--data=" + json.loads(open("testin", "r").read())["data"])
    result = subprocess.run(prefix + params, stdout=subprocess.PIPE, text=True)
    print(result.stdout)
    pass
