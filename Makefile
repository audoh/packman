docker_cmd = docker-compose -f docker/docker-compose.test.yml run packman-test
pytest_cmd = pytest --testdox ${PYTEST_ARGS}


define run_docker_command
	$(docker_cmd) $(1)
endef

# To run commands without debug output:
# bash: PYTEST_ARGS=-q make watch --quiet 2> /dev/null
# powershell: $PYTEST_ARGS="-q"; make watch --quiet 2> $null

# Default: installs the project and starts the watcher
.PHONY: quickstart
quickstart:
	make install watch

# Installs the project
.INTERMEDIATE: install
install: .venv

# Compiles the packaged binary
build: .venv $(wildcard packman/**/*.py) $(wildcard packman_cli/**/*.py)
	poetry run python -m nuitka --follow-imports packman_cli/cli.py --output-dir=build
	cp build/cli.bin bin/packman.bin 2> /dev/null || true
	cp build/cli.exe bin/packman.exe 2> /dev/null || true

# Builds Docker
.PHONY: docker
docker:
	docker-compose -f docker/docker-compose.test.yml up --build 1>&2

# Generates JSON schema and any other auto-generated docs
.PHONY: docs
docs:
	poetry run python docs/build/main.py
	mkdocs gh-deploy

# Checks code for code style issues etc.
.PHONY: lint
lint:
	poetry run flake8 packman packman_cli packman_gui

# Builds Docker and lints
.PHONY: lint-docker
lint-docker:
	make docker
	$(call run_docker_command,make lint)

# Runs all tests
.PHONY: tests
tests:
	make docker
	$(call run_docker_command,$(pytest_cmd))

# Alias for make tests
.PHONY: test
test:
	make tests

# Starts an interactive session
.PHONY: cli
cli:
	poetry run python -m packman_cli.cli

# Starts a GUI session
.PHONY: gui
gui:
	poetry run python -m packman_gui.gui

# Runs lint and test
.PHONY: checks
checks:
	make lint tests

# Runs checks when anything changes
.PHONY: watch
watch:
	poetry run python -c print\(\'...\',end=\'\\r\'\)
	make docker
	poetry run python watcher.py -p . -c 'make docker && $(docker_cmd) $(pytest_cmd)'

.venv: poetry.lock
	poetry install
