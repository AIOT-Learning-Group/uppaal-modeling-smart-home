import json
import os
import tempfile
from typing import List, Literal, Optional
from typing_extensions import TypedDict
from loguru import logger
from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
from modeling.animation import build_anim_spec
from service.utils import range_requests_response, save_to_archives

router = APIRouter()

GenerationRequest = TypedDict(
    'GenerationRequest', {"tap_rules": str, "senario_traces": str, })


@router.post("/api/generate-animation-specification", response_class=PlainTextResponse)
async def generate_animation_specification(request: Request) -> str:
    gen_request: GenerationRequest = await request.json()
    tap_rules = gen_request["tap_rules"]
    senario_traces = gen_request["senario_traces"]
    logger.info(f"input trace length: {len(senario_traces)}")
    specification = json.dumps(build_anim_spec(
        senario_traces, tap_rules), indent=2)
    save_to_archives("specifications", os.path.basename(
        tempfile.NamedTemporaryFile().name), specification)
    logger.info(f"output specification length: {len(specification)}")
    return specification

RenderingTask = TypedDict('RenderingTask', {
    'token': str,
    'status': Literal["pending", "processing", "finished", "failed", "canceled"],
    'input': str,
    'result': str,  # PATH TO FILE IF NOT FAILED
    'assignee': str
})

task_queue: List[RenderingTask] = []
machines = 0


@router.post("/api/add-rendering-task", response_class=PlainTextResponse)
async def add_rendering_task(request: Request) -> str:
    # TODO: add layout info from input
    token = os.path.basename(tempfile.NamedTemporaryFile().name)
    task_queue.append({
        'token': token,
        'status': "pending",
        'input': str(await request.body(), "utf-8"),
        'result': "",
        'assignee': ""
    })
    return token


@router.get("/api/query-rendering-task-status", response_class=PlainTextResponse)
async def query_rendering_task_status(token: str) -> str:
    for task in task_queue:
        if task["token"] == token:
            return task["status"]
    return ""


@router.get("/api/query-rendering-task-assignee", response_class=PlainTextResponse)
async def query_rendering_task_assignee(token: str) -> str:
    for task in task_queue:
        if task["token"] == token:
            return task["assignee"]
    return ""


@router.get("/api/cancel-rendering-task")
async def cancel_rendering_task(token: str) -> None:
    for task in task_queue:
        if task["token"] == token:
            task["status"] = "canceled"


@router.get("/api/pull-rendering-result")
def pull_rendering_result(token: str, request: Request) -> Response:
    for task in task_queue:
        if task["token"] == token and task["status"] == "finished":
            return range_requests_response(
                request, file_path=task["result"], content_type="video/mp4"
            )
    return Response(status_code=404)


@router.get("/api/fake-rendering-result")
def fake_rendering_result(token: str, request: Request) -> Response:
    return range_requests_response(
        request, file_path="demo2.mp4", content_type="video/mp4"
    )


@router.get("/api/pull-rendering-task")
async def pull_rendering_task(server_name: str) -> Optional[RenderingTask]:
    for task in task_queue:
        if task["status"] == "pending":
            task["status"] = "processing"
            task["assignee"] = server_name
            logger.info(f"assign {task['token']} to {server_name}")
            return task
    logger.info(f"{server_name} asks for task, but nothing exists.")
    return None


@router.post("/api/push-rendering-result")
async def push_rendering_task(token: str, request: Request) -> None:
    for task in task_queue:
        if task["token"] == token:
            video_data = await request.body()
            task["status"] = "finished"
            task["result"] = save_to_archives(
                "animation", task["token"], video_data)
            logger.info(f"save {token} to {task['result']}")
            return
    logger.warning(f"task {token} not found")
