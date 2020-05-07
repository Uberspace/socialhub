SRCDIR=src

.PHONY: build
build:
	rm -f dist/*
	python setup.py sdist bdist_wheel
	tox --installpkg dist/socialhub-*.tar.gz

.PHONY: upload
upload:
	twine upload -u uberspace dist/*

.PHONY: test
test:
	tox

.PHONY: quicktest
quicktest:
	py.test

.PHONY: lint
lint:
	pre-commit run -a

.PHONY: devsetup
devsetup:
	pip install -e .
	pip install -r requirements.dev.txt
	pre-commit install --overwrite --install-hooks

.PHONY: recordvcr
recordvcr:
	rm -f socialhub/cassette/*/*.yaml
	make quicktest
