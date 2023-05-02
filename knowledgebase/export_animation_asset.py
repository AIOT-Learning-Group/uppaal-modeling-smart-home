from google.protobuf import text_format

from knowledgebase.animation_asset_base_pb2 import AnimationAssetBase, AppearanceState, AppearanceStateMachine, AppearanceTransition

if __name__ == "__main__":
    base = AnimationAssetBase()
    machine = AppearanceStateMachine()
    machine.name = "Humidifier"
    machine.initial_state_name = "hoff"
    machine.states.extend([
        AppearanceState(name="hon", prefab_name="onPic"),
        AppearanceState(name="hoff", prefab_name="offPic")
    ])
    machine.transitions.extend([
        AppearanceTransition(
            trigger_name="turn_hum_on", prev_state_name="hoff", next_state_name="hon", prefab_name="off2onPre"
        ),
        AppearanceTransition(
            trigger_name="turn_hum_off", prev_state_name="hon", next_state_name="hoff", prefab_name="off2onPre"
        )
    ])
    base.appearance_state_machine.append(machine)
    f = open('knowledgebase/animation_asset_base.textproto', 'w')
    print(text_format.MessageToString(base))
    f.write(text_format.MessageToString(base))
    f.close()
