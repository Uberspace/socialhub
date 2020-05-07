# SocialHub

![PyPI](https://img.shields.io/pypi/v/socialhub)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/socialhub)

Simple API client for [SocialHub]'s API.

[SocialHub]: https://socialhub.io/

## Development

### Setup

1. clone the repo

```console
$ git clone git@github.com:Uberspace/socialhub.git
$ cd socialhub
$ python3 -m venv venv
$ source venv/bin/activate
```

2. install dependencies and commit-hooks

```console
$ make devsetup
pip install -r requirements.txt -r requirements.dev.txt
Collecting requests==2.23.* (from -r requirements.txt (line 1))
  Using cached https://files.pythonhosted.org/packages/1a/70/1935c770cb3be6e3a8b78ced23d7e0f3b187f5cbfab4749523ed65d7c9b1/requests-2.23.0-py2.py3-none-any.whl
(...)
  Running setup.py install for pyyaml ... done
  Running setup.py install for distlib ... done
  Running setup.py install for wrapt ... done
Successfully installed appdirs-1.4.3 aspy.yaml-1.3.0 (...)
pre-commit install --overwrite --install-hooks
pre-commit installed at .git/hooks/pre-commit
```

### Testing

We're using py.test. You can run all of the tests on all supported python
releases using `make test`. If you don't have that much time, try
`make quicktest`, which runs `py.test` directly.

#### API Requests

The tests make use of [vcrpy], which records all requests to the SocialHub APIs
into the `socialhub/cassette` directory. As long as you don't add any,
this enables you to run the existing tests without having access to these
(private) APIs.

To delete the recorded data and get fresh version, run the following command.
Inspect the resuling cassettes for secret leaks.

```console
$ make recordvcr
```

[vcrpy]: https://vcrpy.readthedocs.io/

### Releasing a new version

Assuming you have been handed the required credentials, a new version
can be released as follows.

1. adapt the version in ``setup.py``, according to `semver`_.
2. commit this change as ``Version 1.2.3``
3. tag the resulting commit as ``v1.2.3``
4. push the new tag as well as the ``master`` branch
5. update the package on PyPI:

```console
$ make build
$ make upload
```

## Disclaimer

This API client is not developed, endorsed or validated by SocialHub or its
developer maloon GmbH. The name "SocialHub" is owned by maloon GmbH, not by the
authors of this library.
