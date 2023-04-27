dev:
	poetry run flask --app page_analyzer:app run
install:
		poetry install
package-install:
		pip install --user dist/*.whl --force-reinstall
lint:
		poetry run flake8 page_analyzer
test:
		poetry run pytest
test-coverage:
		poetry run pytest --cov=app --cov-report xml tests
selfcheck:
		poetry check

check:		selfcheck test lint

build:
		poetry build

publish:
	        poetry publish --dry-run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
