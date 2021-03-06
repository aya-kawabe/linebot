import json
import os
from logging import DEBUG, StreamHandler, getLogger

import requests

import falcon

# logger
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

ENDPOINT_URI = 'https://trialbot-api.line.me/v1/events'


class CallbackResource(object):
    # line
    header = {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Line-ChannelID': os.environ['LINE_CHANNEL_ID'],
        'X-Line-ChannelSecret': os.environ['LINE_CHANNEL_SECRET'],
        'X-Line-Trusted-User-With-ACL': os.environ['LINE_CHANNEL_MID'],
    }

    def on_post(self, req, resp):

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        receive_params = json.loads(body.decode('utf-8'))
        logger.debug('receive_params: {}'.format(receive_params))

        for msg in receive_params['result']:

            logger.debug('msg: {}'.format(msg))

            send_content = {
                'to': [msg['content']['from']],
                'toChannel': 1383378250,  # Fixed value
                'eventType': '138311608800106203',  # Fixed value
                'content': {
                    'contentType': 1,
                    'toType': 1,
                    'text': [msg['content']['from']],
                },
            }
            send_content = json.dumps(send_content)
            logger.debug('send_content: {}'.format(send_content))

            res = requests.post(ENDPOINT_URI, data=send_content, headers=self.header)
            logger.debug('res: {} {}'.format(res.status_code, res.reason))

            resp.body = json.dumps('OK')


api = falcon.API()
api.add_route('/callback', CallbackResource())
