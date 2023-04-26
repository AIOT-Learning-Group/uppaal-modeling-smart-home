import json
import os
import tempfile
from typing import List, Literal, TypedDict
from loguru import logger
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from modeling.animation import build_anim_spec

router = APIRouter()


@router.post("/api/generate-animation-specification", response_class=PlainTextResponse)
async def generate_animation_specification(request: Request) -> str:
    traces = str(await request.body(), 'utf-8')
    logger.info(f"trace length: len({traces})")
    return json.dumps(build_anim_spec(traces))

RenderingTask = TypedDict('RenderingTask', {
    'token': str,
    'status': Literal["pending", "processing", "finished", "failed", "canceled"],
    'input': str,
    'result': str  # PATH TO FILE IF NOT FAILED
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
        'result': ""
    })
    return token


@router.get("/api/query-rendering-task", response_class=PlainTextResponse)
async def query_rendering_task(token: str) -> str:
    for task in task_queue:
        if task["token"] == token:
            return task["status"]
    return "notfound"


@router.get("/api/cancel-rendering-task")
async def cancel_rendering_task(token: str) -> None:
    for task in task_queue:
        if task["token"] == token:
            task["status"] = "canceled"


@router.get("/api/pull-rendering-result", response_class=PlainTextResponse)
async def pull_rendering_result(token: str) -> str:
    # TODO: return video data
    for task in task_queue:
        if task["token"] == token:
            return task["result"]
    return ""


@router.post("/api/pull-rendering-task")
async def pull_rendering_task(request: Request) -> None:
    pass


@router.post("/api/push-rendering-result")
async def push_rendering_task(request: Request) -> None:
    pass


# @router.post("/api/reg-rendering-machine")
# async def reg_rendering_machine(request: Request) -> None:
#     pass


# @router.get("/api/count-rendering-machine")
# async def count_rendering_machine(request: Request) -> None:
#     pass
