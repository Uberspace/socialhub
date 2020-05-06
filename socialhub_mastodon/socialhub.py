import dataclasses
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

    def create_ticket(self, message: str, network_item_id: str):
        self.post('/inbox/tickets', json={
            'interaction': {
                'message': message,
                'networkItemId': network_item_id,
            }})
