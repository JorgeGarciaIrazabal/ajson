clear-build:
	rm -rf build/ & rm -rf dist/ & rm -rf  ajson.egg-info

sdist:
	python setup.py sdist bdist_wheel

upload: clear-build  sdist
	twine upload dist/*
	rm -rf build/ & rm -rf dist/ & rm -rf ajson.egg-info

deploy-hotfix:
	python deploy.py hotfix

deploy-minor:
	python deploy.py minor

deploy-mayor:
	python deploy.py mayor

deploy:
	python deploy.py