import json
import re
import requests

# Proxied to www.coursera.org/api/workspaceSubmissions.v1 via gateway.
COURSERA_SUBMISSION_URL = 'https://hub.coursera-apps.org/api/workspaceSubmissions.v1'
BATCH_CREATE_ACTION = '?action=createBatch'

def submit(submission_token, schema_name, schema_names):
    try:
        schema_names_list = json.loads(schema_names)
        if not schema_names_list:
            response = requests.post(
                COURSERA_SUBMISSION_URL,
                data=json.dumps({'token': submission_token, 'schemaName': schema_name}),
                timeout=10,
            )
        else:
            response = requests.post(
                COURSERA_SUBMISSION_URL + BATCH_CREATE_ACTION,
                data=json.dumps({'token': submission_token, 'schemaNames': schema_names_list}),
                timeout=10,
                )
    except Exception as err:
        return 'Failed to execute submission request: {}'.format(err)

    if response.status_code == 201:
        return response.json()['elements'][0]['message']
    elif response.status_code == 200:
        return response.json()['message']
    elif response.status_code < 500:
        return 'Bad request:\n{}'.format(response.json())
    else:
        error_id, = re.findall(
            'This exception has been logged with id <strong>(.+)</strong>',
            response.text)
        return 'Unexpected server error logged with id {}. '.format(error_id) + \
               'Please contact Coursera support.'
