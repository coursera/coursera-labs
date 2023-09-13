#!/bin/bash

NBGRADER_LEARNER="learner"
ASSIGNMENT_NAME="test-files"
GRADER_FILES="$UNIT_TEST_FILES_PATH/grader"

mkdir -p unit-test-env/submitted/$NBGRADER_LEARNER/$ASSIGNMENT_NAME 
cd unit-test-env
cp -r $GRADER_FILES/. submitted/$NBGRADER_LEARNER/
cp $GRADER_FILES/gradebook.db gradebook.db
cp $GRADER_FILES_PATH/scoreCalculator.py scoreCalculator.py
cp $GRADER_FILES_PATH/scrub.py scrub.py
cp $GRADER_FILES_PATH/preamble.html preamble.html

# Create submission folder for assignment
mkdir -p "submitted/$NBGRADER_LEARNER/$ASSIGNMENT_NAME"

# Allow authors to add custom nbgrader config by adding nbgrader_config.py under `/release`
if [ -e "$UNIT_TEST_FILES_PATH/nbgrader_config.py" ]; then
    echo "Using instructor defined nbgrader_config"
    cp $UNIT_TEST_FILES_PATH/nbgrader_config.py nbgrader_config.py    
else
    # Generate empty config
    nbgrader generate_config --quiet
fi

echo "Autograding assignments (this may take a few seconds)..."

# Autograde the submission with nbgrader
nbgrader autograde --assignment="$ASSIGNMENT_NAME" --create --force &> autograde.log
echo "Cat autograde"
cat autograde.log
# Generate the rich feedback for the assignment
nbgrader generate_feedback "$ASSIGNMENT_NAME" &> feedback.log
echo "Cat feedback"
cat feedback.log
