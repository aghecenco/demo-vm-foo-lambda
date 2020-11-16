import base64
import boto3
import datetime
import json
import urllib3

import jwt

from utils import *


GITHUB_APP_ID = 88873
GITHUB_APP_INST_ID = 12999207 # does this change?
GITHUB_APP_INST_URL = 'https://api.github.com/app/installations/{}'.format(GITHUB_APP_INST_ID)
GITHUB_REPO = 'https://api.github.com/repos/aghecenco/demo-vm-foo'

USER_AGENT = 'demo-long-running-tests'
SECRET = 'demo-foo-issue-maker.2020-11-16.private-key.pem'


def secret_key():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
    )
    s = client.get_secret_value(SecretId=SECRET)
    secret_dict = eval(s['SecretString'])
    return secret_dict[SECRET]


def mkjwt(key):
    now = datetime.datetime.utcnow()
    jwt_payload = {
        'iat': now,
        'exp': now + datetime.timedelta(minutes=10),
        'iss': GITHUB_APP_ID
    }
    return jwt.encode(jwt_payload, key, algorithm='RS256').decode()


def github_app_token():
    response = urllib3.PoolManager().request(
        'POST',
        '{}/access_tokens'.format(GITHUB_APP_INST_URL),
        headers={
            'Authorization': 'Bearer {}'.format(mkjwt(secret_key())),
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': USER_AGENT
        }
    )
    return eval(response.data)['token']


def post_github_issue(github_token, issue_data):
    http = urllib3.PoolManager()
    issue_data_enc = json.dumps(issue_data).encode('utf-8')
    response = http.request(
        'POST',
        '{}/issues'.format(GITHUB_REPO),
        headers={
            'Authorization': 'token {}'.format(github_token),
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT
        },
        body=issue_data_enc
    )
    print('Issue created')
    print(response.data.decode('utf-8'))


def on_build_passed(evt_body):
    # TODO: who cares?
    print('Build passed!')
    return get_response_dict(STATUS_OK, 'Build passed', {})


def on_build_failed(evt_body):
    print('Build failed!')
    
    issue_data = { 'title': 'Long running tests failed' }
    post_github_issue(github_app_token(), issue_data)
    
    return get_response_dict(STATUS_OK, 'Build failed', {})


def process_evt(evt_body):
    if evt_body['build']['state'].strip().lower() == 'passed':
        return on_build_passed(evt_body)
    elif evt_body['build']['state'].strip().lower() == 'failed':
        return on_build_failed(evt_body)

    return get_response_dict(STATUS_BAD_REQUEST,\
                                 'Error: Invalid build status!\n',\
                                 {})


def lambda_handler(event, context):
    bad_hdr = validate_header(event)
    if bad_hdr:
        return bad_hdr
    
    body = json.loads(event['body'])
    
    bad_body = validate_body(body)
    if bad_body:
        return bad_body

    return process_evt(body)
