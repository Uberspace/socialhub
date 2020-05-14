import dataclasses
import hashlib
import hmac
import time
import typing
from urllib.parse import urljoin

import requests


class SocialHubError(Exception):
    def __init__(self, response):
        self.status_code = response.status_code
        self.code = response.json()['code']
        self.message = response.json()['message']

    def __str__(self):
        return f'{self.status_code}/{self.code}: {self.message}'


class SocialHubSignatureError(Exception):
    pass


class SocialHubSignatureTimestampError(SocialHubSignatureError):
    pass


class SocialHubEntity():
    def json_dict(self):
        assert dataclasses.is_dataclass(self)

        d = dataclasses.asdict(self)

        for k in list(d.keys()):
            if k.endswith('_'):
                d[k[:-1]] = d[k]
                del d[k]

        return d


@dataclasses.dataclass
class TicketAction(SocialHubEntity):
    type_: str
    id_: str
    label: str


@dataclasses.dataclass
class TicketInteractor(SocialHubEntity):
    interactorId: str
    name: str
    url: str
    picture: str


class SocialHub():
    API_BASE = 'https://api.socialhub.io/'

    def __init__(self, accesstoken):
        self.accesstoken = accesstoken

        self.session = requests.session()
        self.session.params.update({'accesstoken': self.accesstoken})

        self.check_authentication()

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.API_BASE, url)
        response = self.session.request(method, url, *args, **kwargs)

        if response.status_code > 399:
            raise SocialHubError(response)

        return response.json()

    def get(self, url, *args, **kwargs):
        return self.request('GET', url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.request('POST', url, *args, **kwargs)

    def patch(self, url, *args, **kwargs):
        return self.request('PATCH', url, *args, **kwargs)

    def check_authentication(self):
        r = self.get('/')

        if 'channel' not in r:
            raise Exception(
                f'Expected / to return a channel object, but got: {", ".join(r.keys())} f'
                'Check the API status and authentication details.'
            )

        return True

    def get_manifest(self):
        return self.get('/')['manifest']

    def set_ticket_actions(self, actions: typing.List[TicketAction]):
        self.patch('/manifest', json={
            'inbox': {
                'ticketActions': [a.json_dict() for a in actions],
            }
        })

    def set_webhook(self, url: str, secret: str):
        self.patch('/manifest', json={
            'webhook': {
                'url': url,
                'secret': secret,
            }
        })

    def create_ticket(
        self,
        message: str, network_item_id: str, url: str,
        *, root_id: str = None, interactor: TicketInteractor = None,
    ):
        data = {
            'interaction': {
                'message': message,
                'networkItemId': network_item_id,
                'url': url,
            }
        }

        if interactor:
            data['interaction'].update({
                'interactor': interactor.json_dict(),
            })

        if root_id:
            data['interaction'].update({
                'root': {'rootId': root_id}
            })

        response = self.post('/inbox/tickets', json=data)
        return response['_id']

    def followup_success(
        self, ticket_id: str, followup_id: str, network_item_id: str, url: str = None,
    ):
        response = self.post(f'/inbox/tickets/{ticket_id}/replies/{followup_id}/success', json={
            'interaction': {
                'networkItemId': network_item_id,
                'url': url,
            }
        })

        return response['_id']

    def followup_reset(self, ticket_id: str, followup_id: str, action_id: str, reason: str):
        self.post(f'/inbox/tickets/{ticket_id}/reset/{action_id}', json={
            'followupId': followup_id,
            'reason': reason,
        })

    @classmethod
    def verify_webhook_signature(
        cls, secret: str, req_timestamp: int, req_raw_body: bytes, req_signature: str,
        ignore_time: bool = False
    ):
        """
        Verify X-SocialHub-Timestamp / X-SocialHub-Signature headers in webook requests
        and return the challenge, which feeds into X-SocialHub-Challenge.

        Specification: https://socialhub.dev/docs/en/webhooks
        """

        # variable names in this method are not very pythonic, but identical to
        # the ones in the PHP implementation. please keep them this way.

        assert type(secret) is str
        assert type(req_timestamp) is int
        assert type(req_raw_body) is bytes
        assert type(req_signature) is str

        secret = secret.encode('ascii')

        req_age = abs(time.time() - req_timestamp/1000)

        if req_age > 300 and not ignore_time:
            raise SocialHubSignatureTimestampError()

        challenge = hashlib.sha256(str(req_timestamp).encode() + b';' + secret).hexdigest()

        signature_hmac = hmac.new(challenge.encode(), digestmod=hashlib.sha256)
        signature_hmac.update(req_raw_body)
        expected_signature = signature_hmac.hexdigest()

        if req_signature != expected_signature:
            raise SocialHubSignatureError()

        return challenge
