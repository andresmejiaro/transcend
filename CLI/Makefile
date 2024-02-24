# Makefile

VENV_NAME := venv
VENV_ACTIVATE := $(VENV_NAME)/bin/activate

.PHONY: run install venv clean

run: venv
	@mkdir -p db/files
	@. $(VENV_ACTIVATE); python main.py --login

install: venv
	@. $(VENV_ACTIVATE); pip install -r requirements.txt

venv: $(VENV_ACTIVATE)

$(VENV_ACTIVATE): requirements.txt
	python3 -m venv $(VENV_NAME)
	@. $(VENV_ACTIVATE); pip install --upgrade pip
	@touch $(VENV_ACTIVATE)

clean:
	rm -rf $(VENV_NAME)
	find . -name "__pycache__" -exec rm -rf {} +
