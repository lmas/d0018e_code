# Setup a new python env (if not existing)
env:
	test -d .venv || python -m venv .venv

# Run webserver locally
run:
	source .venv/bin/activate
	python app.py

# Install pip and requirements
deps:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

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
