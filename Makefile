.PHONY: unit unit-debug purge-pyc

unit:
	nosetests --tests tests --verbosity 3

unit-debug:
	nosetests --tests tests --verbosity 3 -s

unit-continuous:
	ASYNC_TEST_TIMEOUT=2 sniffer

purge-pyc:
	find . -name "*.pyc" -delete;
