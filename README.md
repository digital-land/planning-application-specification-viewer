# planning-application-specification-viewer
## Specification API smoke test

Activate the `spec-viewer` virtual environment and install the local API:

```sh
python -m pip install -e /Users/colm/code/mhclg/digital-land/planning-application-data-specification
```

From this repository, run:

```sh
python -I scripts/smoke_test_specification.py /Users/colm/code/mhclg/digital-land/planning-application-data-specification
```

The test loads a field, module, application, codelist and guidance through the installed API. It reports the interpreter, package location, editable installation status and data path. A failure exits with an error. This checks the API connection; full viewer rendering and parity are subsequent work.
