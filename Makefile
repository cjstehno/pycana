.PHONY: clean dist

clean:
	find . -name '*.py[co]' -delete

virtualenv:
	python -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt
	.venv/bin/python setup.py develop
	@echo
	@echo "VirtualENV Setup Complete. Now run: source .venv/bin/activate"
	@echo

test:
	python -m pytest \
		-v \
		--cov=pycana \
		--cov-report=term \
		--cov-report=html:coverage-report \
		tests/

lint:
	python -m pylint pycana

format:
	python -m black -l 120 pycana tests

check: format lint test

dist: clean check
	rm -rf dist/*
	python -m build --no-isolation
