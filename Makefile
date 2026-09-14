PYTHON ?= python
SPEC_ROOT ?= ../planning-application-data-specification

.PHONY: install smoke-test

install:
	$(PYTHON) -m pip install -e "$(SPEC_ROOT)"
	$(PYTHON) -m pip install -e .

smoke-test:
	$(PYTHON) -I scripts/smoke_test_specification.py "$(SPEC_ROOT)"
