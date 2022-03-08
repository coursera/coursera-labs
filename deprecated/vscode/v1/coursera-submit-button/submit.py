from coursera.grading import submit
import os
import sys

schema_names = sys.argv[1].split(',')
print(schema_names)
submission_token = os.environ.get('SUBMISSION_TOKEN')
if len(schema_names) == 0:
    print('Failed to find which assignment to submit to.')
elif submission_token is None:
    print('Failed to find submission token. Please contact Coursera support.')
else:
    print(submit(submission_token, schema_names))
