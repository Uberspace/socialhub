SRCDIR=src

.PHONY: test
test:
	py.test

.PHONY: lint
lint:
	pre-commit run -a

.PHONY: devsetup
devsetup:
	pip install -r requirements.txt -r requirements.dev.txt
	pre-commit install --overwrite --install-hooks
