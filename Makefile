.PHONY: requirements run_test

requirements:
	rm -rf version_env
	python3 -m venv version_env
	version_env/bin/pip3 install -r requirements.txt
	version_env/bin/pip3 install coverage pytest pytest-env pytest-mock moto==4.2.14

run_test:
	$(MAKE) requirements
	PYTHONPATH='.' version_env/bin/coverage run -m pytest -s -c local_pytest.ini --verbose ./tests/unit/
	version_env/bin/coverage report -m --omit=tests/*
	rm -rf version_env
