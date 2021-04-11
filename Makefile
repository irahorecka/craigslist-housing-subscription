black: ## Black format every python file to line length 100
	find . -type f -name "*.py" | xargs black --line-length=100;
	make clean;

flake: ## Flake8 every python file
	find . -type f -name "*.py" -a | xargs flake8;

pylint: ## pylint every python file
	find . -type f -name "*.py" -a | xargs pylint;

clean: ## Remove pycache
	find . -type d -name "__pycache__" | xargs rm -r;
