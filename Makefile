# FileName:   Makefile
# Author:     Fasion Chan
# @contact:   fasionchan@gmail.com
# @version:   $Id$
#
# Description:
#
# Changelog:
#

egg:
	python setup.py egg_info

wheel:
	python setup.py sdist

build: libase setup.py
	python setup.py build

clean:
	rm -rf build
	rm -rf dist
	rm -rf libase.egg-info

upload: clean wheel
	twine upload dist/*
