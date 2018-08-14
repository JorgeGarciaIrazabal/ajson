

clear-build:
	rm -rf build/ & rm -rf dist/

sdist:
	python setup.py sdist bdist_wheel

upload-test: clear-build sdist
	twine upload dist/* -r testpypi

upload: sdist
	twine upload dist/*
