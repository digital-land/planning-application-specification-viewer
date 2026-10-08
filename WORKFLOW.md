# Generated site workflow

`.github/workflows/render-static-site.yml` builds on non-docs pushes to `main`, manually and daily at 05:17 UTC (08:17 in Africa/Addis_Ababa). Daily runs pick up newly published specification prereleases and current project documents; an upstream push alone does not trigger this repository.

## Specification release selection

Each run checks out the viewer only. The release selector paginates the source repository's GitHub Releases, ignores drafts and non-prereleases, and selects the most recently published tag exactly matching `YYYY.M.D.devN` with a valid calendar date. An optional manual `release_tag` must identify an eligible published prerelease. The selector resolves that tag to a commit SHA, and pip installs the package from the immutable Git commit. With no eligible release, the workflow fails and does not use `main` as a fallback. A Git tag without a published GitHub Release is not eligible. Official releases are currently excluded too.

Publishing a specification release does not immediately trigger this workflow; the next daily run discovers it, or a viewer source push or manual run triggers selection. Use the manual `release_tag` input to reproduce an older eligible prerelease.

At mandation, official specification releases should use dated versions without `.devN`. Update this viewer's release-selection policy before consuming those releases; the current selector intentionally accepts only dated development prereleases.

## Project content and generated output

The separate `fetch-project-content` step resolves the source repository's `main` branch to a commit and downloads the design-decision Markdown and reporting CSV into a managed cache. Actions cache restore/save carries its change history between successful runs. The fetch metadata records `checked_at` separately from `last_updated`, so a repeat fetch does not claim unchanged content was revised. Tests and the bundled API smoke test must pass before generating a fresh site. The action replaces `/docs`, including stale generated files, and commits only changed generated output. `build-provenance.json` records the specification version, tag and commit and the separate project-content ref and commit; it excludes fetch times to keep identical content builds stable.

The hosted base URL is `/planning-application-specification-viewer`. Change it if publishing under a custom domain or another path. The progress JSON's input path is a stable source-relative path to prevent runner paths causing daily commits; HTML is unaffected.

The workflow needs permission to push to `main`; repository rules must permit its generated commits. Concurrent render runs are serialised. An intervening human push causes a safe non-fast-forward failure instead of overwriting work; rerun on the latest branch.

This workflow generates and commits files; it does not deploy GitHub Pages. GitHub documents that commits made with `GITHUB_TOKEN` do not trigger a Pages build from a branch. Configure an explicit Pages deployment workflow when publishing is wanted: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

Dependency lock updates remain reviewed source changes. If the upstream package adds dependencies, `pip check` fails until the locks are updated rather than silently changing the environment.

## Open scope decision: support for multiple specification versions

The viewer currently generates one selected specification version at a time. Each successful build replaces the generated site. Selecting an older release manually changes that single output; it does not make several versions available side by side.

Before supporting multiple versions, decide:

- whether to publish only the current version, all official versions or a limited set
- whether development prereleases should remain available after the specification becomes mandatory
- how long to retain older versions and what support each receives
- whether older sites are preserved as built or rebuilt with later renderer fixes
- how users choose a version, which version opens by default and how version-specific URLs remain stable
- whether project documents and reporting data should reflect the time of each release or remain current

Retaining release tags makes the source available, but does not by itself provide a browsable site or promise renderer compatibility for every version. This decision is deferred; the current scope remains one generated version.
