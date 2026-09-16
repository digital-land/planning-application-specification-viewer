# Generated site workflow

`.github/workflows/render-static-site.yml` builds on non-docs pushes to `main`, manually and daily at 05:17 UTC (08:17 in Africa/Addis_Ababa). Daily runs pick up upstream specification changes; an upstream push alone does not trigger this repository.

Each run checks out the viewer and the specification's `main` branch into separate runner directories, installs the checked-in dependency locks in a virtual environment and installs both Python packages. Tests and the API smoke test must pass before generating a fresh site. The action replaces `/docs`, including removing stale generated files, and commits only changed generated output. The commit records the specification revision. No local specification checkout or locally generated docs commit is required.

The hosted base URL is `/planning-application-specification-viewer`. Change it if publishing under a custom domain or another path. The progress JSON's input path is normalised to a stable source-relative path in CI to prevent runner paths causing daily commits; HTML is unaffected.

The workflow needs permission to push to `main`; repository rules must permit its generated commits. Concurrent render runs are serialised. An intervening human push causes a safe non-fast-forward failure instead of overwriting work; rerun on the latest branch.

This workflow generates and commits files; it does not deploy GitHub Pages. GitHub documents that commits made with `GITHUB_TOKEN` do not trigger a Pages build from a branch. Configure an explicit Pages deployment workflow when publishing is wanted: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

Dependency lock updates remain reviewed source changes. If the upstream package adds dependencies, `pip check` fails until the locks are updated rather than silently changing the environment.
