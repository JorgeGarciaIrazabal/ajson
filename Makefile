clear-build:
	rm -rf build/ & rm -rf dist/ & ajson.egg-info

sdist:
	python setup.py sdist bdist_wheel

upload: clear-build  sdist
	twine upload dist/*
	rm -rf build/ & rm -rf dist/ & ajson.egg-info
