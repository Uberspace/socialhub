import dataclasses
import os
import time

import pytest

from .socialhub import SocialHub
from .socialhub import SocialHubEntity
from .socialhub import SocialHubError
from .socialhub import TicketAction


@pytest.fixture(scope='module')
def vcr_config():
    return {
        'filter_query_parameters': [('accesstoken', 'XXX_filtered_accesstoken_XXX')],
    }


@pytest.fixture(scope='module')
def vcr_cassette_dir(request):
    return os.path.join('socialhub_mastodon/cassette', request.module.__name__)


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
    client.create_ticket('foo', f'social-mastodon-test-{int(time.time()*1000)}')


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
