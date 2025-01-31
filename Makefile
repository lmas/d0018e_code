# Setup a new python env (if not existing)
env:
	test -d .venv || python -m venv .venv

# Install pip and requirements
deps:
	. .venv/bin/activate && python -m pip install --upgrade pip
	. .venv/bin/activate && python -m pip install -r requirements.txt

# Run webserver locally
run:
	. .venv/bin/activate && python example/app.py

# Run tests and save coverage stats
test:
	pytest --cov

# Generate fancy coverage report
coverage:
	coverage html -d .html

# Run static analysis (aka linting) and find common errors
lint:
	pycodestyle --max-line-length 120 *.py

# Autoformat python code
format:
	black --line-length 120 *.py

# Run local webserver
serve:
	python backend.py

# Clean up leftovers
clean:
	rm -rf .pytest_cache/
	rm -f .coverage
	rm -rf .html/
	find ./ -iname '*.pyc' | xargs rm -f
	find ./ -iname '__pycache__' | xargs rm -rf
