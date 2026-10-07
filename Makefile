PYTHON ?= python
SPEC_ROOT ?=
PACKAGE_SOURCE ?= ../planning-application-data-specification
PROJECT_ROOT ?= project-content
SOURCE_REF ?= main
PINNED_PIP := 25.2
PINNED_PIPTOOLS := 7.5.1

.PHONY: init install tooling requirements sync smoke-test

init: tooling
	$(MAKE) requirements
	$(MAKE) sync

install: init

tooling:
	$(PYTHON) -m pip install --upgrade "pip==$(PINNED_PIP)" "setuptools>=68" "wheel>=0.42" "build>=1.0.0"
	$(PYTHON) -m pip install "pip-tools==$(PINNED_PIPTOOLS)"

requirements:
	$(PYTHON) -m piptools compile --resolver=backtracking --output-file=requirements/requirements.txt requirements/requirements.in "$(PACKAGE_SOURCE)/pyproject.toml"
	$(PYTHON) -m piptools compile --allow-unsafe --resolver=backtracking requirements/dev-requirements.in

sync:
	$(PYTHON) -m piptools sync requirements/dev-requirements.txt requirements/requirements.txt
	$(PYTHON) -m pip install --no-deps --no-build-isolation "$(PACKAGE_SOURCE)" -e .
	$(PYTHON) -m pip check

smoke-test:
	$(PYTHON) -I scripts/smoke_test_specification.py $(if $(SPEC_ROOT),"$(SPEC_ROOT)",)

BASE_URL ?=
PORT ?= 8081
.PHONY: build fetch-project-content serve tests

build:
	$(PYTHON) -m spec_viewer.build $(if $(SPEC_ROOT),--spec-root "$(SPEC_ROOT)",) --project-root "$(PROJECT_ROOT)" --base-url "$(BASE_URL)"

fetch-project-content:
	$(PYTHON) -m spec_viewer.project_content --ref "$(SOURCE_REF)" --cache "$(PROJECT_ROOT)"

serve:
	$(PYTHON) -m http.server $(PORT) --directory docs --bind 127.0.0.1

tests:
	$(PYTHON) -m pytest -q
