import json
from loguru import logger
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from modeling.animation import build_anim_spec

router = APIRouter()


@router.post("/api/generate-animation-specification", response_class=PlainTextResponse)
async def generate_animation_specification(request: Request) -> None:
    traces = str(await request.body(), 'utf-8')
    logger.info(f"trace length: len({traces})")
    return json.dumps(build_anim_spec(traces))
