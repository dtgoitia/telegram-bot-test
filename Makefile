PYTHON_DIR:=.

run_dtg_bot:
	docker-compose run --rm dtg_bot

rebuild_bot:
	docker-compose build telegram-bot

shell_bot:
	docker-compose run --rm telegram-bot bash

compile_production_dependencies:
	find ./requirements -type f -name "prod.txt" -delete
	pip-compile requirements/prod.in \
		--output-file requirements/prod.txt \
		--no-header \
		--no-emit-index-url \
		--verbose

compile_development_dependencies:
	find ./requirements -type f -name "dev.txt" -delete
	pip-compile requirements/prod.in requirements/dev.in \
		--output-file requirements/dev.txt \
		--no-header \
		--no-emit-index-url \
		--verbose

install_production_dependencies:
	pip install -r requirements/prod.txt

install_development_dependencies:
	pip install -r requirements/dev.txt

lint:
	flake8
	black --check --diff $(PYTHON_DIR)
	isort --check --diff $(PYTHON_DIR)
	python -m mypy --config-file setup.cfg --pretty $(PYTHON_DIR)

format:
	isort $(PYTHON_DIR)
	black $(PYTHON_DIR)

test:
	pytest $(PYTHON_DIR)/tests -vv
