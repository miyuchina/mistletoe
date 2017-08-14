.PHONY: run test coverage integration benchmark

run:
	python3 -m mistletoe

test:
	python3 -m unittest

coverage:
	. venv/bin/activate && \
	python3 -m coverage run -m unittest && \
	coverage report && \
	deactivate

integration:
	./test/test_ci.sh 1

benchmark:
	python3 test/benchmark.py
