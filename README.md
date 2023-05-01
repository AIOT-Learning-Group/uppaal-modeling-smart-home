
## Environment setup

```
pip install -r requirements.txt
```

Then extract `libs.zip` and move all jar files into epg_service_jar

Now you can run server by

```
uvicorn main:app --host=0.0.0.0 --reload
```

## Compile proto files

[ProtoBuf](https://github.com/protocolbuffers/protobuf) is used in this project, to automatically generate parser for our knowledge base for different programming languages. You need to install protoc and mypy-protobuf to ensure correct type annotation.

You can install mypy-protobuf by

```
pip install mypy-protobuf
```

The `protoc` binary can be downloaded from [here](https://github.com/protocolbuffers/protobuf/releases).

After adding the path of bin folder unzipped from archive into env `PATH`, you should be able to compile proto files by

```
./compile_proto.sh
```

## How to add a device model

Device Models are the instance of `ComposableTemplate` in `modeling.common`.

1. Add constructor function in `modeling.device`, for example `build_two_state_device_with_impacts`
2. Register the constructor function with its parameters in `knowledgebase/system_device_modes.proto`
3. Run `./compile_proto.sh`.
4. Update function `modeling.device.build_from_pb` to use paramters to call your constructor function.
5. Save all related parameters into the file in `config.KNOWLEDGEBASE_DEVICE_TABLE` as textproto. `modeling.export_device_table` gives an example for exporting parameters from code.
6. Remeber to check the `modeling.rule.valid_device_names` and other assertions before commit.

## Contribution

**Please ensure that your code has been checked by autopep8 and has passed static type checks by running `./check.sh` before you make any commit.**
