TOP = ..
CUR_DIR := $(shell pwd)

include $(TOP)/configure/CONFIG
include $(CONFIG)/RULES_DIRS

clean distclean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~'    -exec rm --force {} +
	find . -name '__pycache__'  -exec rm -rd --force {} +
