VENV_DIR = venv
REQUIREMENTS_FILE = requirements.txt
MAIN_SCRIPT = main.py

.PHONY: venv install run

venv:
	python3 -m venv $(VENV_DIR)

install: venv
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS_FILE)

run: install
	$(VENV_DIR)/bin/python3 $(MAIN_SCRIPT)

clean:
	rm -rf $(VENV_DIR)

.PHONY: clean
