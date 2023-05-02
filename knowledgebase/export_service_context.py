from google.protobuf import text_format
from knowledgebase import service_context_models_pb2
from knowledgebase.service_context_models_pb2 import ServiceContext, ServiceContextModels, EnvAttribute

if __name__ == "__main__":
    models = ServiceContextModels()

    context = ServiceContext()
    context.name = "Smart Home(6 Locations Layout)"

    context.env_attributes.extend(
        [EnvAttribute(name="Environment Temperature"), EnvAttribute(name="Environment Humidity")])
    context.locations.extend(
        ["out", "living_room", "kitchen", "bathroom", "bedroom", "guest_room"])
    f = open('knowledgebase/service_context_models.textproto', 'w')
    models.context.append(context)
    print(text_format.MessageToString(models))
    f.write(text_format.MessageToString(models))
    f.close()
