.PHONY: install test docs clean

install:
	pip install -e ".[dev,docs]"

test:
	pytest tests/

docs:
	cd docs && make html

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf docs/_build/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
