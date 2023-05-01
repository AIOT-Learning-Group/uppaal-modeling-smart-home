
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

## Contribution

**Please ensure that your code has been checked by autopep8 and has passed static type checks by running `./check.sh` before you make any commit.**
