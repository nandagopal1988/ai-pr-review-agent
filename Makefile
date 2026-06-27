.PHONY: install test lint format clean run help

help:
	@echo "Code Review Agent - Available Commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make run          - Run the agent"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run in Docker"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/ config/
	isort src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache build dist *.egg-info .coverage htmlcov

run:
	python src/code_review_agent.py

docker-build:
	docker build -t code-review-agent:latest .

docker-run:
	docker run --rm \
		-e GITHUB_TOKEN \
		-e GITHUB_REPOSITORY \
		-e OPENAI_API_KEY \
		-e SONARQUBE_ENABLED=false \
		code-review-agent:latest

analyze-pr:
	python src/cli/analyze_rules.py $(PR_NUMBER)

sonarqube:
	python src/cli/analyze_sonarqube.py

llm-review:
	python src/cli/review_with_llm.py --pr-number $(PR_NUMBER)

extract-changes:
	python src/cli/extract_changes.py --pr-number $(PR_NUMBER)
