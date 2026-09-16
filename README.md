# Planning application specification viewer

A static site for exploring the planning application data standard. The viewer generates HTML from the installed [specification package and source data](https://github.com/digital-land/planning-application-data-specification), with its own rendering code, templates and presentation content.

The site includes the homepage, application types, modules, components, fields, codelists, datasets, views, user needs, justifications, design decisions, examples and submission progress. It also generates downloadable example JSON and a sitemap.

## Local setup

Use Python 3.13 to match the dependency locks and GitHub Actions environment. Run these commands from the viewer repository in a dedicated virtual environment:

```sh
python3.13 -m venv .venv
source .venv/bin/activate
make tooling
make sync
make smoke-test
make tests
```

An existing dedicated `spec-viewer` environment can be used instead. `make sync` removes packages outside the locked requirements, so do not run it in a shared environment.

`SPEC_ROOT` defaults to the sibling `../planning-application-data-specification` repository. For another source location, pass the same root during installation and building:

```sh
make sync SPEC_ROOT=/path/to/planning-application-data-specification
make smoke-test SPEC_ROOT=/path/to/planning-application-data-specification
make build SPEC_ROOT=/path/to/planning-application-data-specification
```

Pass the repository root, not its `specification/` subdirectory. The source supplies the Python package, specification data, canonical guidance, needs, example JSON, design-decision documents and coverage CSV. Local development currently requires these files; CI fetches its own source checkout. A build-input archive can replace that checkout later.

## Build and preview

```sh
make build
make serve
```

Open [the local site](http://localhost:8081/). The output directory is `docs/` at the viewer repository root, configured in `pyproject.toml`. Override the preview port with `make serve PORT=8082`.

For hosted URLs:

```sh
make build BASE_URL=/planning-application-specification-viewer
```

The simple preview server expects a local-root build, so run `make build` without `BASE_URL` before using `make serve`.

For a fresh output directory:

```sh
python -m spec_viewer.build \
  --spec-root ../planning-application-data-specification \
  --output /tmp/spec-viewer-preview
python -m http.server 8081 --directory /tmp/spec-viewer-preview --bind 127.0.0.1
```

Local builds do not delete old output: removed source records can leave stale pages behind. Use a fresh directory for comparisons. **Do not commit locally generated `docs/` files.** Generated-page commits belong to the GitHub Actions workflow.

## Automated generation

The [render workflow](.github/workflows/render-static-site.yml) runs on non-docs pushes to `main`, daily at 05:17 UTC and manually. It checks out both repositories, installs the locked dependencies and packages, runs tests and the API smoke test, then builds a fresh site. It replaces `docs/`, removes stale generated files and commits only changed output, recording the specification revision.

Daily runs pick up upstream specification changes. A change in the specification repository does not immediately trigger the viewer workflow.

The workflow generates and commits files; it does not deploy GitHub Pages. Its first GitHub run and Pages publishing setup remain to be verified/configured. See [workflow details](WORKFLOW.md) for permissions, concurrency, dependency updates and deployment considerations.

## Repository structure

```text
src/spec_viewer/
    build.py          Build orchestration and command-line entry point
    data.py           Package-backed specification and needs loading
    rendering.py      Shared templates, filters, URLs and assets
    pages/            Page-family rendering
    view_models/      Presentation adapters and project reporting
 templates/           Page layouts, components and macros
 content/             Viewer-specific example explanations
 static/              CSS, JavaScript, fonts and images
 requirements/        pip-tools inputs and dependency locks
 tests/               Renderer and reporting tests
 scripts/             API smoke test
 docs/                Generated site, committed by CI only
```

Templates, content and static assets are currently loaded from the viewer checkout. Installing the Python package alone as a wheel is not yet sufficient to run the viewer.

## Data and content boundaries

`load_viewer_data(source)` loads specification models through `Specification.load()` and needs/justifications through the package's separate `loader.load_needs()` API. Page builders share those loaded inputs.

```python
from spec_viewer.data import load_viewer_data

data = load_viewer_data("/path/to/planning-application-data-specification")
spec = data.specification
field = spec.field("description")
usages = spec.field_usages("description")
guidance = spec.guidance(dataset="decision-notice", field="planning-officer-recommendation")
```

Specification rules should live in the package. Some compatibility adapters still interpret package-loaded metadata for application field inheritance, profile/view overrides and need relationships. Combined-application ordering also reads source CSV metadata. These preserve the original output while package improvements are considered.

Project documents are a separate concern: the viewer reads design-decision Markdown directly without exposing it through the specification API. Example explanations live in `content/`; their canonical JSON remains in the source repository. Coverage reporting reads the source volume CSV and uses package application references. No viewer code imports the original repository's `bin` modules or modifies Python's search path.

See [content and reporting ownership](CONTENT-MIGRATION.md) for the full split and the outstanding decision about the progress page's longer-term home.

## Dependencies

`requirements/requirements.in` declares viewer runtime dependencies. `requirements/dev-requirements.in` adds test dependencies. Both generated `.txt` lock files are committed.

- `make tooling` installs pip-tools and build tooling.
- `make requirements` recompiles the locks, including dependencies declared by the source package's `pyproject.toml`.
- `make sync` installs the locks and both packages in editable mode, then runs `pip check`.
- `make init` runs tooling, recompilation and sync; `make install` is an alias.

Use `make init` when intentionally refreshing dependencies, and review the resulting lock changes. CI installs existing locks rather than recompiling them.

## Validation and known issues

`make tests` runs the automated suite. `make smoke-test` checks the installed package, explicit source path and access to fields, modules, applications, codelists, guidance, needs and justifications. It reports package location and editable-install status.

The completed migration was checked against specification commit `2093c2b129d091aed1c91b9da9a0f41b3caf6a78`: all 1,038 output files, including 1,005 HTML pages, matched byte-for-byte for root and hosted URLs. This is a frozen-baseline result; current source content can produce different counts. The suite had 39 passing tests at migration completion.

Shared layouts and assets retain their original provenance, including GOV.UK Frontend 6.4.0 and the external Digital Land CSS/JavaScript URLs. Existing behaviour was preserved for parity. [Known frontend bugs](BUGS.md) record the nested-accordion and search-restoration issues.
