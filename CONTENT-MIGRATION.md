# Content and reporting ownership

The viewer now renders the homepage, design decisions, examples and submission progress, completing the frozen page inventory.

| Material | Current location and responsibility |
| --- | --- |
| Page layouts and homepage prose | Viewer `templates/` |
| Example navigation | Viewer `view_models/examples.py` |
| Example explanations | Viewer `content/example/` and `content/dataset/` |
| Canonical example JSON | Source `specification/example/`, read and copied to downloadable output at build time |
| Design decision Markdown | Source `documentation/design-decisions/`, read directly by the viewer; no specification package API needed |
| Coverage volumes and source notes | Source `bin/admin_data/2024-application-volumes.csv` |
| Coverage calculation and display | Viewer `view_models/progress.py` and progress template, preserving legacy reporting rules |
| Specification definitions and guidance | Source repository, accessed through the installed package |

The source repository has not been edited or had files deleted. Moving presentation here means establishing the viewer's own rendering sources, not removing the old renderer before migration is complete.

## Progress page decision still to make

The progress page remains for mirror parity. Its reporting rules include inheritance-only references and an explicit covered combination exception. These are project reporting choices, not general specification API requirements. Decide later whether the reporting calculation should remain here or consume a separately produced coverage report. The CSV stays with the source project for now; the viewer passes package application references explicitly and never imports source `bin` code or infers a checkout from the current directory.

## Build inputs

A source directory is still required during migration. A versioned archive or other distributed input can replace the separate checkout later. This does not require exposing project documentation through the specification package.
