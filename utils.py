STATUS_BAD_REQUEST = 400
STATUS_OK = 200

BUILDKITE_REQ_HDR = 'buildkite-request'
BUILDKITE_BUILD_FIN = 'build.finished'
BUILDKITE_PIPELINE = 'f945dadf-c001-4551-962f-65766820759c'


def get_response_dict(status_code, body, headers):
    return {
        'statusCode': status_code,
        'body': body,
        'headers': headers
    }


# Check the header and return a 400 response if it's invalid.
# Return None if the header is OK.
def validate_header(event):
    if not 'headers' in event:
        return get_response_dict(STATUS_BAD_REQUEST,\
                                 'Error: Request was sent with no headers!\n',\
                                 {})
    
    if not 'user-agent' in event['headers']:
        return get_response_dict(STATUS_BAD_REQUEST,\
                                 'Error: Request was sent without user-agent header!\n',\
                                 {})
    
    if event['headers']['user-agent'].strip().lower() != BUILDKITE_REQ_HDR:
        return get_response_dict(STATUS_BAD_REQUEST,\
                                 'Error: Request was sent with invalid user-agent header!\n',\
                                 {})

    if not 'x-buildkite-event' in event['headers']:
        return get_response_dict(STATUS_BAD_REQUEST,\
                                 'Error: Request was sent without x-buildkite-event header!\n',\
                                 {})
    
    if event['headers']['x-buildkite-event'].strip().lower() != BUILDKITE_BUILD_FIN:
        return get_response_dict(STATUS_BAD_REQUEST,\
                                 'Error: Request was sent with invalid x-buildkite-event header!\n',\
                                 {})    
    return None


def validate_body(evt_body):
    if evt_body['event'].strip().lower() != BUILDKITE_BUILD_FIN:
        return get_response_dict(STATUS_BAD_REQUEST,\
                                 'Error: Request was sent for invalid event!\n',\
                                 {})

    if evt_body['pipeline']['id'] != BUILDKITE_PIPELINE:
        return get_response_dict(STATUS_BAD_REQUEST,\
                                 'Error: Request was sent for invalid pipeline!\n',\
                                 {})
    return None
