.PHONY: run test coverage

run:
	python3 main.py

test:
	python3 -m unittest

coverage:
	. venv/bin/activate && \
	python3 -m coverage run -m unittest && \
	coverage report && \
	deactivate
