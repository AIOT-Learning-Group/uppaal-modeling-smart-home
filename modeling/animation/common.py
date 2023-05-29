
from typing import List, Tuple, TypedDict


RawTraceFrame = Tuple[float, float]
KeyFrame = TypedDict(
    'KeyFrame', {'type': int, 'name': str, "animation": str, "timestamp": float})
AnimationSpecification = TypedDict('AnimationSpecification', {
                                   'keyFrames': List[KeyFrame]})
