from modeling.human import HumanModelForSmartHome
from modeling.rule import valid_device_names, on_off_devices_names, open_close_devices_names
from typing_extensions import TypedDict, NotRequired
from typing import Dict, List, Optional
from fastapi import APIRouter

router = APIRouter()

SystemDeviceModels = ["Common Smart Home Devices"]
SystemContextModels = ["Air Environment"]
AnimationAssetBases = [
    "Smart Home(3 Locations Layout)", "Smart Home(6 Locations Layout)"]


@router.get("/api/list-system-device-model")
async def list_system_device_model():
    return {"result": SystemDeviceModels}


@router.get("/api/list-system-context-model")
async def list_system_context_model():
    return {"result": SystemContextModels}


@router.get("/api/list-animation-asset-bases")
async def list_animation_asset_bases():
    return {"result": AnimationAssetBases}


Specification = TypedDict(
    'Specification', {'subject': str, 'predicates': NotRequired[List[str]], "placeholder": NotRequired[str]})
env_triggers: List[Specification] = [
    {
        "subject": "temperature",
        "placeholder": "[<=>] 20"
    },
    {
        "subject": "pm_2_5",
        "placeholder": "[<=>] 50"
    },
    {
        "subject": "brightness",
        "placeholder": "[<=>] 300"
    },
    {
        "subject": "time",
        "placeholder": "[<=>] 100"
    },
]


human_trigger: Specification = {
    "subject": "HumanPosition",
    "predicates": [f".{loc}" for loc in HumanModelForSmartHome.locations]
}


@router.get("/api/get-trigger-specs")
async def get_trigger_specs() -> List[Specification]:
    return [human_trigger, *env_triggers, *get_device_func_spec(True)]


@router.get("/api/get-action-specs")
async def get_action_specs() -> List[Specification]:
    return get_device_func_spec()


on_off_devices_names = [
    "fan", "airpurifier", "light",  "camera", "humidifier",
]

open_close_devices_names = [
    "door", "curtain", "window",
]

special_devices_names = [
    "ac", "SMS"
]


def get_device_func_spec(include_state: bool = False) -> List[Specification]:
    devices_numbers: Dict[str, int] = {
        "fan": 1, "airpurifier": 1, "light": 2, "camera": 1, "humidifier": 1,
        "door": 2, "curtain": 2, "window": 2,
        "ac": 1, "SMS": 1
    }
    device_func_spec: List[Specification] = []
    for device, number in devices_numbers.items():
        assert device in valid_device_names
        if device in on_off_devices_names:
            for i in range(number):
                device_func_spec.append(
                    {
                        "subject": f"{device}_{i}",
                        "predicates": [
                            ".on", ".off",
                            f".turn_{device}_on",
                            f".turn_{device}_off"
                        ] if include_state else [
                            f".turn_{device}_on",
                            f".turn_{device}_off"
                        ]
                    },
                )
        elif device in open_close_devices_names:
            for i in range(number):
                device_func_spec.append(
                    {
                        "subject": f"{device}_{i}",
                        "predicates": [
                            ".open", ".close",
                            f".open_{device}",
                            f".close_{device}"
                        ] if include_state else [
                            f".open_{device}",
                            f".close_{device}"
                        ]
                    },
                )
        elif device == "ac":
            for i in range(number):
                device_func_spec.append(
                    {
                        "subject": f"ac_{i}",
                        "predicates": [
                            ".off", ".cool", ".heat",
                            ".turn_ac_off",
                            ".turn_ac_cool",
                            ".turn_ac_heat"
                        ] if include_state else [
                            ".turn_ac_off",
                            ".turn_ac_cool",
                            ".turn_ac_heat"
                        ]
                    }
                )
        elif device == "SMS":
            device_func_spec.append(
                {
                    "subject": "SMS",
                    "predicates": [
                        ".send_msg",
                    ]
                }
            )
    return device_func_spec
