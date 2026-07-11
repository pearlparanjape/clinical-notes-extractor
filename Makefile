install:
	poetry install

test:
	poetry run pytest

lint:
	poetry run flake8 src tests
	poetry run black --check src tests

format:
	poetry run black src tests