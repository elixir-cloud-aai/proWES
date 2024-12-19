default: help

# Color variables
BOLD = \033[1m
PURPLE = \033[35m
GRAY = \033[37m
CYAN = \033[36m
NC = \033[0m

.PHONY: help
help:
	@echo "\nUsage: make [target] ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
	@echo "Available targets:\n"
	@echo "Development Environment ---------------------------------------------------"
	@echo "  ${BOLD}${PURPLE}clean-venv${NC} ${GRAY}(cv)${NC}: ${CYAN}Remove virtual environment.${NC}"
	@echo "  ${BOLD}${PURPLE}install${NC} ${GRAY}(i)${NC}: ${CYAN}Install package in development mode.${NC}"
	@echo "  ${BOLD}${PURPLE}venv${NC} ${GRAY}(v)${NC}: ${CYAN}Create virtual environment.${NC}\n"
	@echo "Development Services -----------------------------------------------------"
	@echo "  ${BOLD}${PURPLE}dev-app${NC} ${GRAY}(da)${NC}: ${CYAN}Run only the prowes Flask app locally.${NC}"
	@echo "  ${BOLD}${PURPLE}dev-celery${NC} ${GRAY}(dc)${NC}: ${CYAN}Run only the Celery worker locally.${NC}"
	@echo "  ${BOLD}${PURPLE}dev-docker${NC} ${GRAY}(dd)${NC}: ${CYAN}Run all docker dev services.${NC}"

# Development Environment
.PHONY: clean-venv cv
clean-venv cv:
	@echo "Removing virtual environment..."
	rm -rf .venv

.PHONY: install i
install i:
	@echo "Installing package in development mode..."
	pip install -e .

.PHONY: venv v
venv v:
	@echo "Creating virtual environment..."
	python -m venv .venv
	@echo "Run 'source .venv/bin/activate' to activate the virtual environment"

# Development Services
.PHONY: dev-docker dd
dev-docker dd:
	@echo "Starting Flask app..."
	docker compose -f docker-compose.dev.yaml up -d

.PHONY: dev-app da
dev-app da:
	@echo "Starting FOCA app..."
	python pro_wes/app.py

.PHONY: dev-celery dc
dev-celery dc:
	@echo "Starting Celery worker..."
	cd pro_wes && celery -A celery_worker worker -E --loglevel=info

.PHONY: lint fl
lint fl:

	@echo "1.Formatting with black..."
	black --exclude .venv pro_wes/ setup.py tests/
	@echo "\n\n2.Checking style with flake8..."
	black --exclude .venv pro_wes/ setup.py tests/
	@echo "\n\n3.Running pylint..."
	pylint pro_wes/ setup.py

.PHONY: type-check tc
type-check tc:
	@echo "Running mypy..."
	mypy pro_wes/ setup.py