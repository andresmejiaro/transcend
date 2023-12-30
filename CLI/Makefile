VENV_DIR := venv
REQUIREMENTS_FILE := requirements.txt
MAIN_SCRIPT := main.py
PYTHON := python3

.PHONY: venv install run clean activate run-existing-venv

venv:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV_DIR)

install: venv
	@echo "Installing dependencies..."
	@$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS_FILE)

run: install
	@echo "Running $(MAIN_SCRIPT)..."
	@$(VENV_DIR)/bin/python3 $(MAIN_SCRIPT)

clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV_DIR)

# If venv already exists, just run the main script
run-existing-venv:
	@echo "Running $(MAIN_SCRIPT) with existing virtual environment..."
	@$(VENV_DIR)/bin/python3 $(MAIN_SCRIPT)

# Print the command to activate the virtual environment
activate:
	@echo "To activate the virtual environment, run:"
	@echo "source $(VENV_DIR)/bin/activate"

# Default target: run, but also print the activation command
default: run activate
