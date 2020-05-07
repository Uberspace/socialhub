# SocialHub Mastodon

Integrate the social network [mastodon] into [SocialHub].

[mastodon]: https://joinmastodon.org/
[SocialHub]: https://socialhub.io/

## Development

### Setup

1. clone the repo

```console
$ git clone git@github.com:Uberspace/socialhub-mastodon.git
$ cd socialhub-mastodon
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

```console
$ make test
```

#### API Requests

The tests make use of [vcrpy], which records all requests to the SocialHub APIs
into the `socialhub_mastodon/cassette` directory. As long as you don't add any,
this enables you to run the existing tests without having access to these
(private) APIs.

To delete the recorded data and get fresh version, run the following command.
Inspect the resuling cassettes for secret leaks.

```console
$ make recordvcr
```

[vcrpy]: https://vcrpy.readthedocs.io/
