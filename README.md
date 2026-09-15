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

The output directory is declared as `docs` in `pyproject.toml` under `[tool.spec-viewer]`. The renderer must use this setting when implemented. The build generates the data-model landing page and field, module, component and codelist indexes and detail pages, plus shared static assets. Other page families are not implemented yet, so navigation to them will not resolve in this partial build.

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
make init
```

From this repository, run:

```sh
python -I scripts/smoke_test_specification.py /Users/colm/code/mhclg/digital-land/planning-application-data-specification
```

The test uses the viewer loading layer to load a field, module, application, codelist, guidance, needs and justifications through the installed API. It reports the interpreter, package location, editable installation status and data path. A failure exits with an error. This checks the API connection; full viewer rendering and parity are subsequent work.

## Shared rendering

`spec_viewer.rendering.create_environment()` configures shared templates, filters and base-path-aware links. `copy_static(output_dir)` copies the publishable assets. Field page orchestration lives in `pages/fields.py`, with presentation adapters in `view_models/fields.py`.

The shared layout, components, macros, usage partial and styles originate from specification commit `2093c2b129d091aed1c91b9da9a0f41b3caf6a78`. GOV.UK Frontend 6.4.0 is vendored with its existing provenance files. The layout retains the current external Digital Land CSS/JavaScript URLs for parity.

Run shared rendering checks with `python -m pytest -q` after `make init`.

## Reading the specification

Page builders load their inputs once and share the returned package models:

```python
from spec_viewer.data import load_viewer_data

data = load_viewer_data("/path/to/planning-application-data-specification")
spec = data.specification
field = spec.field("description")
fields = spec.fields.values()
usage = spec.field_usages("description")
guidance = spec.guidance(dataset="decision-notice", field="planning-officer-recommendation")
needs = data.needs
justifications = data.justifications
```

Pass the repository root, not its `specification/` subdirectory. The loader uses the installed package's `Specification.load` and `loader.load_needs`; it does not parse source files, change directories or infer a checkout location. Display sorting, links and formatting belong in the view models added with each page family. Missing paths and package loading errors propagate to the caller.

## Build and preview

```sh
make build
make serve
```

Open `http://localhost:8081/field/`. `make build` writes to the configured repository-root `docs/` directory. Supply `SPEC_ROOT=/path/to/specification` to choose the data checkout, or `BASE_URL=/planning-application-specification-viewer` to build hosted-subpath URLs. The simple preview server serves local-root builds. For alternative output locations use `python -m spec_viewer.build --spec-root /path/to/specification --output /path/to/output`.

The build does not delete existing output. Use a fresh output directory for migration comparisons; removed source fields can otherwise leave old generated pages behind. It does not publish or push anything.

## Data model pages

`pages/data_model.py` renders the data-model landing page and module, component and codelist families. `view_models/containers.py` presents the package's resolved container items and contextual guidance. `view_models/codelists.py` presents codelist metadata, source links and package usage results. Codelist pages preserve the original metadata/source-link presentation without adding value tables.

Index pages only initialise the reusable `index-search.js` component. Application-type, dataset, needs and other page families remain to be migrated, so links to those pages do not resolve in this partial site.
