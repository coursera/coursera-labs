import json
import re
import requests

COURSERA_SUBMISSION_URL = 'https://hub.labs.coursera.org/api/workspaceSubmissions.v1'
BATCH_CREATE_ACTION = '?action=createBatch'

def submit(submission_token, schema_names):
    try:
        response = requests.post(
            COURSERA_SUBMISSION_URL + BATCH_CREATE_ACTION,
            data=json.dumps({'token': submission_token, 'schemaNames': schema_names}),
            timeout=10,
        )
    except Exception as err:
        return 'Failed to execute submission request: {}'.format(err)

    if response.status_code == 200:
        return '{} \nGo to the assignment page in your course to see your submissions.'.format(
            response.json()['message'])
    elif response.status_code < 500:
        return 'Bad request:\n{}'.format(response.json())
    else:
        error_id, = re.findall(
            'This exception has been logged with id <strong>(.+)</strong>',
            response.text)
        return 'Unexpected server error logged with id {}. '.format(error_id) + \
            'Please contact Coursera support.'
