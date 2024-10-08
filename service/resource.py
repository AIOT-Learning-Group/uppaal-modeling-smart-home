from modeling.human import HumanModelForSmartHome
from modeling.rule import valid_device_names, on_off_devices_names, open_close_devices_names
from typing_extensions import TypedDict, NotRequired
from typing import Dict, List, Optional
from fastapi import APIRouter

router = APIRouter()

SystemDeviceModels = ["Common Smart Home Devices"]
ServiceContextModels = ["Air Environment"]
AnimationAssetBases = [
    "Smart Home(3 Locations Layout)", "Smart Home(6 Locations Layout)"]


@router.get("/api/list-system-device-model")
async def list_system_device_model() -> Dict[str, List[str]]:
    return {"result": SystemDeviceModels}


@router.get("/api/list-service-context-model")
async def list_service_context_model() -> Dict[str, List[str]]:
    return {"result": ServiceContextModels}


@router.get("/api/list-animation-asset-bases")
async def list_animation_asset_bases() -> Dict[str, List[str]]:
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
    "subject": "Human",  # HumanPosition
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
    "ac", "sms"
]


def get_device_func_spec(include_state: bool = False) -> List[Specification]:
    devices_numbers: Dict[str, int] = {
        "fan": 1, "airpurifier": 1, "light": 2, "camera": 1, "humidifier": 1,
        "door": 2, "curtain": 2, "window": 2,
        "airconditioner": 1, "sms": 1
    }
    device_func_spec: List[Specification] = []
    for device, number in devices_numbers.items():
        assert device in valid_device_names, f"{device} not found in valid device names"
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
                            ".turn_airconditioner_off",
                            ".turn_airconditioner_cool",
                            ".turn_airconditioner_heat"
                        ] if include_state else [
                            ".turn_airconditioner_off",
                            ".turn_airconditioner_cool",
                            ".turn_airconditioner_heat"
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
