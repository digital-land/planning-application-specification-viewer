# Planning application specification viewer

An independent static renderer using the installed specification package and an explicit path to specification data.

## Structure

```text
src/spec_viewer/       Python renderer package
    pages/            Page-family orchestration
    view_models/      Presentation adapters for API results
templates/            Page layouts and shared components
content/              Viewer-specific Markdown prose
static/               CSS, JavaScript, fonts and images
tests/                Viewer behaviour tests
scripts/              Development checks
docs/                 Generated site at the repository root
```

The output directory is declared as `docs` in `pyproject.toml` under `[tool.spec-viewer]`. The renderer must use this setting when implemented. No generated site is added by this scaffold. There is no build command yet; add `build.py`, shared rendering code and page implementations with the first working page family.

## Local setup

Activate the existing `spec-viewer` virtual environment, then run:

```sh
make init
make smoke-test
```

`SPEC_ROOT` defaults to the sibling `../planning-application-data-specification` checkout and can be overridden with `make smoke-test SPEC_ROOT=/path/to/specification`.

Keep specification loading and rules in the installed package. Do not import the source repository's `bin` modules or modify Python's search path. Templates, content and static assets are checkout resources at this stage; a standalone distributable viewer wheel is not yet supported.

## Dependency management

`requirements/requirements.in` declares third-party viewer runtime dependencies. Compilation also reads the local specification package's `pyproject.toml`, so its dependencies are locked without duplicating them. Shared rendering uses Jinja, Digital Land Frontend pinned to the baseline Git revision and GOV.UK Frontend Jinja 4.0.0.

`requirements/dev-requirements.in` includes the runtime lock and adds development dependencies. Commit both generated `.txt` files. `make init` installs pip-tools, compiles the locks, syncs the active environment and installs both local packages in editable mode without resolving dependencies again. Run it in the dedicated `spec-viewer` virtual environment because sync removes packages outside the declared requirements.

Use `make requirements` to refresh locks and `make sync` to install the existing locks. `make install` remains an alias for `make init`. `pip check` verifies the local package requirements after installation.

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

## Shared rendering

`spec_viewer.rendering.create_environment()` configures shared templates, filters and base-path-aware links. `copy_static(output_dir)` copies the publishable assets. Page orchestration and the `docs/` build command are the next implementation step.

The shared layout, components, macros, usage partial and styles originate from specification commit `2093c2b129d091aed1c91b9da9a0f41b3caf6a78`. GOV.UK Frontend 6.4.0 is vendored with its existing provenance files. The layout retains the current external Digital Land CSS/JavaScript URLs for parity.

Run shared rendering checks with `python -m pytest -q` after `make init`.
