#!/bin/bash

echo "Environment variables: "
printenv

# For notebook ps1/problem1.ipynb:
# assign_dir = ps1, submitted_filename = submission.ipynb, assign_file = problem1.ipynb, feedback_filename = problem1.html
assign_dir="$assignmentName"
submitted_filename="$filename"
assign_file="$notebookId"
feedback_filename="${assign_file//\.ipynb/.html}"

# URL decode the assignment name and notebook id
DECODED_SUBMISSION="$(echo -n $submitted_filename | python -c "import sys; from urllib.parse import unquote; print(unquote(sys.stdin.read()));")"
ASSIGNMENT_NAME="$(echo -n $assign_dir | python -c "import sys; from urllib.parse import unquote; print(unquote(sys.stdin.read()));")"
NOTEBOOK_FILENAME="$(echo -n $assign_file | python -c "import sys; from urllib.parse import unquote; print(unquote(sys.stdin.read()));")"
DECODED_FEEDBACK="$(echo -n $feedback_filename | python -c "import sys; from urllib.parse import unquote; print(unquote(sys.stdin.read()));")"
DECODED_SUBMISSION_FILENAME=${DECODED_SUBMISSION%.ipynb}

NBGRADER_LEARNER="courseraLearner"

# Copy the mounted grader files to create submission structure 
cd $JN_WORK_DIR
mkdir -p submitted/$NBGRADER_LEARNER
cp -r /shared/grader/. submitted/$NBGRADER_LEARNER/
cp /shared/grader/gradebook.db gradebook.db
cp $GRADER_FILES_PATH/scoreCalculator.py scoreCalculator.py
cp $GRADER_FILES_PATH/scrub.py scrub.py
cp $GRADER_FILES_PATH/preamble.html preamble.html

# Create submission folder for assignment
mkdir -p "submitted/$NBGRADER_LEARNER/$ASSIGNMENT_NAME"

# Copy student assignment from Coursera shared directory
cp "/shared/submission/$DECODED_SUBMISSION" "submitted/$NBGRADER_LEARNER/$ASSIGNMENT_NAME/$NOTEBOOK_FILENAME"

# Get kernel language from the submitted assignment's metadata
kernel_language="$(jq '.metadata.kernelspec.language' "submitted/$NBGRADER_LEARNER/$ASSIGNMENT_NAME/$NOTEBOOK_FILENAME")"

# Allow authors to add custom nbgrader config by adding nbgrader_config.py under /release
if [ -e "/shared/grader/nbgrader_config.py" ]; then
    echo "Using instructor defined nbgrader_config"
    cp /shared/grader/nbgrader_config.py nbgrader_config.py    
else
    # Generate empty config
    nbgrader generate_config --quiet
fi

# Autograde the submission with nbgrader
nbgrader autograde --assignment="$ASSIGNMENT_NAME" --notebook="$DECODED_SUBMISSION_FILENAME" --create --force # &> autograde.log

# Generate the rich feedback for the assignment
nbgrader generate_feedback "$ASSIGNMENT_NAME" &> feedback.log

# Scrub given feedback file to remove hidden tests and tracebacks
# Checks options.json for toggling on/off hiding tests or tracebacks
python scrub.py "$NBGRADER_LEARNER" "$ASSIGNMENT_NAME" "$DECODED_FEEDBACK" "$courseraPartMaxScore" "$kernel_language" "$NOTEBOOK_FILENAME"

# Copy the cleaned feedback to the shared directory
cp "feedback/$NBGRADER_LEARNER/$ASSIGNMENT_NAME/$DECODED_FEEDBACK.clean" /shared/htmlFeedback.html
