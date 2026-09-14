# Viewer migration inventory

Date: 2026-09-14. Task 021, Step 2.

## Outcome and baseline

The current viewer successfully renders from a frozen source snapshot at `2093c2b129d091aed1c91b9da9a0f41b3caf6a78`. Both local-root and `/planning-application-data-specification` builds contain 1,005 HTML pages and 1,038 files. This establishes the existing implementation baseline; replica rendering and visual parity are not yet demonstrated.

The viewer repository started clean at `179257d88e5808567c85576b91405164e90c3ded`. The specification repository had no tracked modifications and its existing untracked files were excluded. The baseline includes the committed field, codelist, application-type and design-decision search work. No source files were edited or generated in the source checkout.

Evidence is under `tmp/baseline-2093c2b1/`: `baseline.json` records revision, working-tree state and exact build commands; `dependencies.txt` records the baseline environment; `local-manifest.json` and `hosted-manifest.json` enumerate every generated path and SHA-256 hash. `source/` is a Git archive of the relevant committed code and inputs. The two output directories are `local/` and `hosted/`. Keep all of this temporary evidence out of commits.

Builds used the existing `pa-explorer` Python 3.10 environment to reproduce the old renderer. The target `spec-viewer` Python 3.13 environment currently contains only the specification package and its loading dependencies; rendering dependencies must be installed there before replica validation. Do not confuse successful baseline rendering with successful target-environment rendering.

## Ownership inventory

Paths below are relative to the specification repository. Keep specification-owned inputs in the frozen snapshot during the first milestone.

| Source | Owner and migration treatment |
| --- | --- |
| `bin/render_static_site.py` | Mixed. Move page orchestration and presentation, replacing local loading and model traversal with installed package calls. Do not copy the whole file unchanged and call it independent. |
| `bin/templates/*.html`, `components/`, `macros/`, `partials/` | Viewer. Preserve page families, shared navigation, phase banner, footer, guidance and example rendering. |
| `bin/templates/content/dataset/*/examples.md` | Viewer editorial introductions and example placement. Move to top-level `content/dataset/`. |
| `bin/templates/content/example/{submission,planning-application-data}/*.md` | Viewer editorial content. Move to `content/example/`, preserving all seven complete-example pages. |
| `bin/assets/` | Viewer. Move CSS, four filtering/search scripts and the vendored GOV.UK 6.4.0 distribution, including fonts, images, source maps and provenance. |
| `bin/renderer.py`, `bin/jinja_filters.py` | Viewer rendering and formatting. Replace `bin.utils.ensure_dir` with a local presentation helper. |
| `bin/markdown_utils.py` | Shared utility with viewer presentation functions. Copy only required Markdown/GOV.UK formatting functions and dependencies; leave unrelated CSV export utilities in the source repo. |
| `bin/dataset_examples.py` | Viewer example presentation, table formatting and placement checks. JSON remains a declared specification-owned read-only input. |
| `bin/loader.py`, `bin/models.py`, transitive `bin/applications.py` | Specification semantics. Do not migrate these implementations. Use package loaders/models and resolved queries. |
| `bin/completeness.py` | Mixed and unresolved: scope/coverage policy plus table formatting. Keep policy in the specification package through a separately approved extension; viewer may own formatting. |
| `bin/admin_data/2024-application-volumes.csv` | Unresolved long-term ownership. Declare as a read-only reporting input for milestone 1. It is not viewer editorial prose or canonical schema data. |
| `specification/{application,module,component,field,dataset,codelist,usage}/` and root schemas/combined types | Specification. Prefer `Specification` model tables and queries rather than duplicate parsing, inheritance or combination rules. |
| `data/codelist/` | Specification. Use package codelist operations. External codelist sources must remain explicit dependencies; do not infer remote data was fetched. |
| `specification/guidance/` | Specification. Use existing guidance API and preserve contextual field/container guidance. |
| `specification/example/` | Specification-owned reusable JSON: dataset records and seven complete downloads. Explicit read-only resource input pending bundled-resource support. |
| `user-needs/{need,justification}/` | Specification. Installed package has `planning_application_specification.loader.load_needs(root_path)`; preserve Markdown bodies and identifier handling. |
| `documentation/design-decisions/*.md` | Specification decisions. Explicit read-only document input; viewer owns title/metadata extraction and presentation. |
| `tests/test_render_static_site_helpers.py`, `tests/test_render_static_site_integration.py`, `tests/test_dataset_examples.py` | Viewer behaviour. Port imports and fixture setup to the new viewer; retain content and base-path regression coverage. |
| `tests/test_markdown_utils.py`, `tests/test_completeness.py` | Split by ownership. Formatting tests can move; coverage-policy tests belong with the policy implementation. |
| `requirements/`, `pyproject.toml` | Mixed. Create focused viewer dependency declarations. Source package currently bundles no data. Avoid importing spreadsheet/schema-generation dependencies merely because they appear in the source requirements. |
| `Makefile` render/copy/serve targets | Viewer build responsibilities. Add explicit source-root and output configuration; never invoke source clean targets against its `docs/`. |
| `.github/workflows/render-static-site.yml` | Existing publication responsibility. Inventory only: currently renders on specification pushes/manual dispatch and commits/pushes `docs`. Publishing transfer belongs to Task 022. |

The templates cover home/data model, datasets, views and explanatory view content, submission/application types, progress, fields, modules, components, codelists, needs, justifications, design decisions and examples, with index/detail variants. Use the generated manifests for exhaustive routes rather than the renderer's partial `sitemap.json`.

## Reads and imports that need attention

The renderer imports eight local helper modules: completeness, dataset_examples, jinja_filters, loader, markdown_utils, models, renderer and utils. Its loader changes working-directory assumptions and compiles a parallel model. Replace this with one explicit `Specification.load(data_root)` and view adapters over package models. The API already exposes fields, modules, components, datasets, applications, raw tables, guidance and usage queries; these are migration work, not automatically API gaps.

Additional reads are root specification/view front matter, application definitions, active combined-application CSV rows, design-decision Markdown, example JSON, viewer editorial Markdown, asset bytes and application-volume CSV. Needs/justifications are currently loaded using working-directory-relative globbing. All input roots must become explicit. Loading canonical data must not depend on importing source `bin` modules or adding the source checkout to `sys.path`.

Application inheritance helpers and active-combination filtering still occur in the renderer. Use existing package application resolution/combination functions where they cover the behaviour. Check differences against the frozen output before changing ordering or interpretation.

The concrete policy gap is progress reporting: `bin/completeness.py` owns inheritance-only reference exceptions, scope inclusion rules, a special covered combination and volume-based coverage calculations. These rules are not supplied by the current public `Specification` API. Do not recreate them in the viewer. A separate source proposal should identify a package-owned progress query, preserve existing CLI behaviour through a thin wrapper and port policy tests. Until approved, report the progress page/data as blocked if other migration work proceeds.

The current base template also loads two CSS files and a JavaScript file from `design.planning.data.gov.uk`. Preserve these declared runtime dependencies for parity, and record their bytes/versions for visual comparison. The baseline render does not establish their network availability. No browser screenshots or interactive verification have yet been performed.

## Next implementation batch

1. Add viewer package structure, focused rendering dependencies, templates, assets and top-level editorial `content/`.
2. Replace old loader/model imports with installed API data and presentation adapters. Keep reusable examples and design decisions as explicit read-only inputs from the same frozen snapshot.
3. Implement all independent page families and retain visible reporting of progress-policy gaps. Prepare a precise source-API proposal rather than copying the policy.
4. Render in `spec-viewer`, compare every route/content/asset with the baseline, inspect template families and exercise search, filters, history, copying and navigation in both base-path configurations.
5. Retain a non-editable installation check. After milestone 1 parity, prepare bundled-resource changes as described in the Task 021 brief. Cutover remains Task 022.

No deployment, push, source modification or permanent parity framework is part of this inventory.

## Baseline regression checks

Ran the following against the frozen snapshot with `pa-explorer`, bytecode disabled and pytest's cache provider disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/colm/.virtualenvs/pa-explorer/bin/python -m pytest -q -p no:cacheprovider tests/test_render_static_site_helpers.py tests/test_render_static_site_integration.py tests/test_dataset_examples.py tests/test_markdown_utils.py tests/test_completeness.py
```

Result: **56 passed, 2 failed** in 44.08 seconds. Both failures occur in the existing snapshot before migration:

- `test_render_site_shows_requirement_levels_for_datasets_and_public_view`: expects `Not specified` in the site dataset page; that text is absent.
- `test_render_site_shows_where_field_is_used`: expects `/component/site-location` in the description field's usage links; that link is absent.

These are recorded baseline assertion/content mismatches. Root cause and whether tests or behaviour should change require separate assessment. Do not silently repair source tests or normalise away these differences during migration.
