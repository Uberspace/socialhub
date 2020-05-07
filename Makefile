SRCDIR=src

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
	pip install -r requirements.txt -r requirements.dev.txt
	pre-commit install --overwrite --install-hooks

.PHONY: recordvcr
recordvcr:
	rm -f socialhub/cassette/*/*.yaml
	make quicktest
