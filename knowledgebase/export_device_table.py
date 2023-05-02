from google.protobuf import text_format
from knowledgebase.system_device_models_pb2 import Device, DeviceTable, TwoStateWithEnvImpactsConstructor

# This is an example to export something build in your code.
if __name__ == "__main__":
    table = DeviceTable()
    EnvImpact = TwoStateWithEnvImpactsConstructor.EnvImpact
    Fan = Device()
    Fan.name = "Fan"
    Fan.ctor_ts.impacts.append(
        EnvImpact(impact_env="dtemperature", impact_rate=-0.02))
    Fan.used_nodes = 2
    table.devices.append(Fan)
    AirPurifier = Device()
    AirPurifier.name = "AirPurifier"
    AirPurifier.ctor_ts.impacts.append(
        EnvImpact(impact_env="dpm_2_5", impact_rate=-0.8))
    AirPurifier.used_nodes = 2
    table.devices.append(AirPurifier)
    f = open('knowledgebase/device_table.pbtxt', 'w')
    print(text_format.MessageToString(table))
    f.write(text_format.MessageToString(table))
    f.close()
