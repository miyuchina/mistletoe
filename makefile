PYTHON_EXEC=python3

.PHONY: run test coverage integration benchmark docs

run:
	${PYTHON_EXEC} -m mistletoe

test:
	${PYTHON_EXEC} -m unittest

coverage:
	. venv/bin/activate && \
	${PYTHON_EXEC} -m coverage run -m unittest && \
	coverage report && \
	deactivate

integration:
	./test/test_ci.sh 1

benchmark:
	${PYTHON_EXEC} test/benchmark.py

specification:
	${PYTHON_EXEC} -m test.specification

docs:
	${PYTHON_EXEC} -m docs

