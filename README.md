
## Environment setup

```
pip install -r requirements.txt
```

Then extract `libs.zip` and move all jar files into epg_service_jar

Now you can run server by

```
uvicorn main:app --host=0.0.0.0 --reload
```

## Contribution

**Please ensure that your code has been checked by autopep8(the default formatter for python in vscode) and has passed static type checks with `mypy modeling --strict && mypy service --strict` before you make any commit.**
