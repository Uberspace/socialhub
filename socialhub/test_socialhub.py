import dataclasses
import os
import time

import pytest

from .socialhub import SocialHub
from .socialhub import SocialHubEntity
from .socialhub import SocialHubError
from .socialhub import SocialHubSignatureError
from .socialhub import SocialHubSignatureTimestampError
from .socialhub import TicketAction


@pytest.fixture(scope='module')
def vcr_config():
    def scrub_headers(*headers):
        def before_record_response(response):
            for header in headers:
                if header in response['headers']:
                    del response['headers'][header]
            return response
        return before_record_response

    return {
        'filter_query_parameters': [('accesstoken', 'XXX_filtered_accesstoken_XXX')],
        'filter_headers': ['Content-Length'],
        'before_record_response': scrub_headers(
            'Date', 'ETag', 'Server', 'Content-Length',
            'X-RateLimit-Limit', 'X-RateLimit-Remaining',
        ),
    }


@pytest.fixture(scope='module')
def vcr_cassette_dir(request):
    return os.path.join('socialhub/cassette', request.module.__name__)


@pytest.fixture()
def accesstoken():
    return os.environ.get('SOCIALHUB_ACCESSTOKEN', 'fake_accesstoken_1337')


@pytest.fixture()
def client(accesstoken):
    return SocialHub(accesstoken)


@pytest.mark.vcr()
def test_ctor(accesstoken):
    SocialHub(accesstoken)


@pytest.mark.vcr()
def test_ctor_wrong_token():
    with pytest.raises(SocialHubError, match='AccessTokenInvalidError'):
        SocialHub('fake_accesstoken_1337')


@pytest.mark.vcr()
def test_get_manifest(client):
    manifest = client.get_manifest()
    assert '_id' in manifest
    assert 'inbox' in manifest


@pytest.mark.vcr()
def test_set_ticket_actions(client):
    client.set_ticket_actions([
        TicketAction('reply', 'reply-public', 'Reply')
    ])
    manifest = client.get_manifest()
    actions = manifest['inbox']['ticketActions']
    assert len(actions) == 1
    assert actions[0]['type'] == 'reply'
    assert actions[0]['id'] == 'reply-public'
    assert actions[0]['label'] == 'Reply'


@pytest.mark.vcr()
def test_set_webhook(client):
    # we can't fully set the hook without hosting a server, but we can at least
    # test that we get past the input validation.
    with pytest.raises(
        SocialHubError,
        match='An error occurred while attempting to validate the WebHook',
    ):
        client.set_webhook('https://example.com/webhook', 't' * 32)


@pytest.mark.vcr()
def test_create_ticket(client):
    client.create_ticket('foo', f'social-test-{int(time.time()*1000)}')


def test_socialhubentity():
    @dataclasses.dataclass
    class TicketAction(SocialHubEntity):
        reserved_field_: str
        unreserved_field: str

    d = TicketAction('reserved_field_value', 'unreserved_field_value').json_dict()
    assert len(d) == 2
    assert 'reserved_field_' not in d
    assert d['reserved_field'] == 'reserved_field_value'
    assert d['unreserved_field'] == 'unreserved_field_value'


def test_verify_webhook_signature():
    challenge = SocialHub.verify_webhook_signature(
        'zieShi0besu7aiZae2mequieveo6ahNg',
        1588761201236,
        b'{"manifestId":"5ea028554e1570519e982403","accountId":"5ea023d6677493519f10710e","channelId":"5ea028554e1570519e982404","events":{}}',  # NOQA
        '836372be68a3d48c99ebb6aec104909e2fc2c5aca3ebe319607f242759124022',
        ignore_time=True
    )
    # generated by the PHP implementation
    assert challenge == '93f4b03366741ddadd603d7ab4155c8891c673e87fc770fd3620d61cb793abab'


def test_verify_webhook_signature_fail():
    with pytest.raises(SocialHubSignatureError):
        SocialHub.verify_webhook_signature(
            'zieShi0besu7aiZae2mequieveo6ahNg',
            1588761201236,
            # "manifest" has a capital M, which it should not have.
            b'{"ManifestId":"5ea028554e1570519e982403","accountId":"5ea023d6677493519f10710e","channelId":"5ea028554e1570519e982404","events":{}}',  # NOQA
            '836372be68a3d48c99ebb6aec104909e2fc2c5aca3ebe319607f242759124022',
            ignore_time=True
        )


def test_verify_webhook_signature_fail_time_past():
    with pytest.raises(SocialHubSignatureTimestampError):
        SocialHub.verify_webhook_signature('xxx', 1588761201236, b'xxx', 'xxx')


def test_verify_webhook_signature_fail_time_future():
    with pytest.raises(SocialHubSignatureTimestampError):
        SocialHub.verify_webhook_signature('xxx', 5588761201236, b'xxx', 'xxx')
