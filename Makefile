.PHONY: unit  # Run unit tests
unit:
	@pytest -v -rf

.PHONY: lint  # Runs linters
lint:
	@echo "Run isort"
	@exec isort --check-only pytest_sqlalchemy_session pytest_sqlalchemy_session_test tests
	@echo "Run black"
	@exec black --check --diff pytest_sqlalchemy_session pytest_sqlalchemy_session_test tests
	@echo "Run flake"
	@exec flake8 pytest_sqlalchemy_session pytest_sqlalchemy_session_test tests
	@exec bandit -r pytest_sqlalchemy_session/*
	@echo "Run mypy"
	@exec mypy pytest_sqlalchemy_session pytest_sqlalchemy_session_test tests

.PHONY: format  # Runs linters and fixes auto-fixable errors
format:
	@echo "Run autoflake"
	@exec autoflake -r -i --remove-all-unused-imports --ignore-init-module-imports pytest_sqlalchemy_session pytest_sqlalchemy_session_test tests
	@echo "Run isort"
	@exec isort pytest_sqlalchemy_session pytest_sqlalchemy_session_test tests
	@echo "Run black"
	@exec black pytest_sqlalchemy_session pytest_sqlalchemy_session_test tests
	@echo "Run flake"
	@exec flake8 pytest_sqlalchemy_session pytest_sqlalchemy_session_test tests
	@echo "Run bandit"
	@exec bandit -r pytest_sqlalchemy_session/*
	@echo "Run mypy"
	@exec mypy pytest_sqlalchemy_session pytest_sqlalchemy_session_test tests


.PHONY: pip-compile # Compile all requirements
pip-compile:
	pip install pip-tools
	pip-compile --verbose --generate-hashes requirements/linters.in


.PHONY: pip-install-dev # Install all requirements
pip-install-dev:
	@pip install -r requirements/base.txt
	@pip install -r requirements/test.txt
	@pip install -r requirements/linters.txt

.PHONY: help  # Help
help:
	@grep '^.PHONY: .* #' Makefile | sed 's/\.PHONY: \(.*\) # \(.*\)/\1	\2/' | expand -t20
