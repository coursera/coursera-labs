#!/bin/bash

NBGRADER_LEARNER="learner"
ASSIGNMENT_NAME="test-files"

if [[ "$#" -ne 1 ]]; then
    echo "Please enter exactly one argument"
    exit
fi

NOTEBOOK_FILENAME="$1_tests.ipynb"
DECODED_FEEDBACK="$1_tests.html"

cd unit-test-env

# Get kernel language from the submitted assignment's metadata
kernel_language="$(jq '.metadata.kernelspec.language' "submitted/$NBGRADER_LEARNER/$ASSIGNMENT_NAME/$NOTEBOOK_FILENAME")"

# Scrub given feedback file to remove hidden tests and tracebacks
# Checks options.json for toggling on/off hiding tests or tracebacks
python scrub.py "feedback/$NBGRADER_LEARNER/$ASSIGNMENT_NAME/$DECODED_FEEDBACK" 100 $kernel_language

# Copy the cleaned feedback to the shared directory
cp "feedback/$NBGRADER_LEARNER/$ASSIGNMENT_NAME/$DECODED_FEEDBACK.clean" ./"$1"_htmlFeedback.html
cp ./"$1"_htmlFeedback.html /shared/

# Validate python feedback
python $UNIT_TEST_FILES_PATH/validateFeedback.py ./"$1"_htmlFeedback.html