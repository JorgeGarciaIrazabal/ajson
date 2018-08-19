clear-build:
	rm -rf build/ & rm -rf dist/

sdist:
	python setup.py sdist bdist_wheel

upload: clear-build  sdist
	twine upload dist/*
