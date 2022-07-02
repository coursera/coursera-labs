#!/bin/bash

NBGRADER_LEARNER="learner"
ASSIGNMENT_NAME="unit-tests"

if [[ "$#" -ne 1 ]]; then
    echo "Please enter exactly one argument"
    exit
fi

NOTEBOOK_FILENAME="$1_tests.ipynb"
DECODED_FEEDBACK="$1_tests.html"

cd unit-test-env

# Scrub given feedback file to remove hidden tests and tracebacks
# Checks options.json for toggling on/off hiding tests or tracebacks
python scrub.py "feedback/$NBGRADER_LEARNER/$ASSIGNMENT_NAME/$DECODED_FEEDBACK" 100

# Copy the cleaned feedback to the shared directory
cp "feedback/$NBGRADER_LEARNER/$ASSIGNMENT_NAME/$DECODED_FEEDBACK.clean" ./"$1"_htmlFeedback.html
cp ./"$1"_htmlFeedback.html /shared/

# Validate python feedback
python $UNIT_TEST_FILES_PATH/validateFeedback.py ./"$1"_htmlFeedback.html