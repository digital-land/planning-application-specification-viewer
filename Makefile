PYTHON ?= python
SPEC_ROOT ?= ../planning-application-data-specification
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
	$(PYTHON) -m piptools compile --resolver=backtracking --output-file=requirements/requirements.txt requirements/requirements.in "$(SPEC_ROOT)/pyproject.toml"
	$(PYTHON) -m piptools compile --resolver=backtracking requirements/dev-requirements.in

sync:
	$(PYTHON) -m piptools sync requirements/dev-requirements.txt requirements/requirements.txt
	$(PYTHON) -m pip install --no-deps --no-build-isolation -e "$(SPEC_ROOT)" -e .
	$(PYTHON) -m pip check

smoke-test:
	$(PYTHON) -I scripts/smoke_test_specification.py "$(SPEC_ROOT)"
