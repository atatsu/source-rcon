.PHONY: unit unit-debug purge-pyc

unit:
	nosetests --tests tests --verbosity 3

unit-debug:
	nosetests --tests tests --verbosity 3 -s

purge-pyc:
	find . -name "*.pyc" -delete;
