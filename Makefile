# Set default workenvironment params
VENV_DIR = virtualenv
VIRTUAL_ENV = ${VENV_DIR}/$(shell basename ${PWD})

python_version = python3.8

# Declare default binary locations
bin = ${VIRTUAL_ENV}/bin
python = ${bin}/python
pip = ${bin}/pip
autopep8 = ${bin}/autopep8
autoflake = ${bin}/autoflake
flake8 = ${bin}/flake8
isort = ${bin}/isort
black = ${bin}/black
pip-compile = ${bin}/pip-compile
pip-sync = ${bin}/pip-sync

all: lint test build deploy

# Environment setup requires python binaries and installed requirements
setup: ${VIRTUAL_ENV}/.requirements.installed | ${python}

# Ensure that when we require python we init our virtual environment
${pip}: | ${python}
${python}:  
	${python_version} -m venv ${VIRTUAL_ENV}

# Ensure that when we require pip-compile, pip-sync or pip we enable pip-tools
${pip-compile} ${pip-sync}: | ${pip}
	${pip} install --quiet pip-tools

# Dependencies are installed using requirements files and require pip-sync for installation
requirements: requirements.txt requirements-dev.txt 

# Requirement txt files are generated from top level requirement (input files)
requirements.txt: requirements.in | ${pip-compile}
	${pip-compile} --output-file $@ $<

requirements-dev.txt: requirements-dev.in | ${pip-compile}
	${pip-compile} --output-file $@ $<

# Check whether requirements are installed and up to date, if not generate and install
requirements = ${VIRTUAL_ENV}/.requirements.installed
${requirements} : requirements.txt requirements-dev.txt | ${pip-sync}
	${pip-sync} requirements.txt requirements-dev.txt
	@touch $@

python_files = $(shell find .  -name "*.py" -not -path "./virtualenv/*")
lint: setup
	${isort} --check-only ${python_files}
	${black} --check ${python_files}
	${flake8} --statistics ${python_files}

# Convenience target for autoformatting
fix: setup
	# sort imports
	${isort} --recursive ${python_files}
	${autoflake} --recursive --in-place --remove-all-unused-imports --remove-unused-variables ${python_files}
	# one style to rule them all (https://github.com/psf/black#the-uncompromising-code-formatter)
	${black} ${python_files}

test: setup
	${python} -m pytest -v tests/

# Build arguments
NAME=btc_7_day_rolling_average_eur
AUTHOR=tvandekeer
VERSION=$(shell git rev-parse --short HEAD)
APP=${NAME}
FULLDOCKERNAME=$(AUTHOR)/$(NAME):latest

build:
	# With the assumption that docker is installed on the host system, the following can be used to build a release of the app
	docker build --no-cache=false -t $(FULLDOCKERNAME) .
	docker tag $(FULLDOCKERNAME) $(AUTHOR)/$(NAME):${VERSION}

run: setup
	${python} app.py

mrproper:
	rm -rf ${VENV_DIR}
	rm -rf __pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest*

