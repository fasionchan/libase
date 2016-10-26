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
	SUBVERSION="$$(cat misc/subversion)" python setup.py sdist

build: libase setup.py
	python setup.py build

clean:
	rm -rf build
	rm -rf dist
	rm -rf libase.egg-info

new_version:
	subversion="$$(cat misc/subversion)" && echo "$${subversion}+1" | bc > misc/subversion

new_wheel: clean new_version wheel

upload: new_wheel
	twine upload dist/*
