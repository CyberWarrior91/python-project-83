dev:
	poetry run flask --app page_analyzer:app run
install:
		poetry install
lint:
		poetry run flake8 page_analyzer
selfcheck:
		poetry check

publish:
	    poetry publish --dry-run

PORT ?= 8000
start:
		psql $(DATABASE_URL) < database.sql
		poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
