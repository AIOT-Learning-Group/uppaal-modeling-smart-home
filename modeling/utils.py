
from typing import TypedDict

translations = {
    "IF": "如果",
    "AND": "并且",
    "THEN": "那么",
    "Human.bedroom": "人在卧室",
    "Human.out": "人出门了",
    "Human.living_room": "人在客厅",
    'Human.bathroom': "人在浴室",
    'Human.kitchen': "人在厨房",
}

NamedDevice = TypedDict(
    'NamedDevice', {'type':str, 'number': int, 'name':str})

open_close_devices: list[NamedDevice] = [
    {'type': 'curtain', 'number': 0, 'name': '客厅窗帘'},
    {'type': 'curtain', 'number': 1, 'name': '卧室窗帘'},
    {'type': 'door', 'number': 0, 'name': '大门'},
    {'type': 'door', 'number': 1, 'name': '卧室门'},
    {'type': 'window', 'number': 0, 'name': '卧室窗'},
]

on_off_devices: list[NamedDevice] = [
    {'type': 'light', 'number': 0, 'name': '客厅顶灯'},
    {'type': 'light', 'number': 1, 'name': '卧室顶灯'},
    {'type': 'light', 'number': 2, 'name': '厨房顶灯'},
    {'type': 'light', 'number': 3, 'name': '浴室顶灯'},
    {'type': 'robotvacuum', 'number': 0, 'name': '卧室扫地机'},
    {'type': 'fan', 'number': 0, 'name': '客厅风扇'},
    {'type': 'coffeemachine', 'number': 0, 'name': '厨房咖啡机'},
    {'type': 'airpurifier', 'number': 0, 'name': '客厅空气净化器'},
    {'type': 'dehumidifier', 'number': 0, 'name': '客厅除湿器'},
    {'type': 'humidifier', 'number': 0, 'name': '客厅加湿器'},
    {'type': 'heater', 'number': 0, 'name': '浴室顶灯'},
]

for device in open_close_devices:
    translations[f"{device['type']}_{device['number']}"] = device['name']
    translations[f"{device['type']}[{device['number']}]"] = device['name']
    translations[f"{device['type']}[{device['number']}]"] = device['name']
    translations[f"open_{device['type']}"] =  "打开"
    translations[f"close_{device['type']}"] =  "关上"

for device in on_off_devices:
    translations[f"{device['type']}_{device['number']}"] = device['name']
    translations[f"{device['type']}[{device['number']}]"] = device['name']
    translations[f"{device['type']}[{device['number']}]"] = device['name']
    translations[f"turn_{device['type']}_on"] =  "开启"
    translations[f"turn_{device['type']}_off"] =  "关闭"

translations.update({
    "temperature": "温度",
    "humidity": "湿度",
    "brightness": "亮度",
    "airquality": "空气质量指数",
    "pm25": "PM2.5",
    "time": "时间",
    " co ": "一氧化碳",
    "airconditioner_0": "客厅空调",
    "airconditioner[0]": "客厅空调",
    "turn_airconditioner_cool": "开制冷",
    "turn_airconditioner_heat": "开制热",
    "turn_airconditioner_off": "关闭",
    "cool": "制冷",
    "heat": "制热",
    "on": "开着",
    "off": "关着",
    "open": "开着",
    "close": "关着",
    "Rule": "规则",
    "human": "人的位置"
})

def translated(text: str):
    for k, v in translations.items():
        text = text.replace(k, v)
    return text

