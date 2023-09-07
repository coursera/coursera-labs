import json
import sys
from nbgrader.api import Gradebook, MissingEntry


def scoreCalculator(assignmentId, notebookName, studentId, testCaseResults):
    # Parse Arguments
    notebookId = notebookName.replace(".ipynb", "")

    # Create the dict we are going to fill
    output = dict()

    # Create the connection to the database
    with Gradebook('sqlite:///gradebook.db') as gb:

        # Try to find the submission in the database. If it doesn't exist, the
        # `MissingEntry` exception will be raised, which means notebook submission is not configured correctly
        try:
            submission = gb.find_submission_notebook(notebookId, assignmentId, studentId)
        except MissingEntry:
            output["fractionalScore"] = 0.0
            output["feedback"] = "Error while grading submission. Please check your submission." 
        else:
            # Calculate score
            if submission.max_score == 0:
                output["fractionalScore"] = 0.0
            else:
                frac_score = submission.score/submission.max_score
                output["fractionalScore"] = frac_score

            # Set the feedback value to show that the grading is complete
            output["feedback"] = "Your assignment has been graded"
            # Set the feedbackType to match the generated feedback
            output["feedbackType"] = "HTML"
            output["testCaseResults"] = str(testCaseResults)


    # jsonify the output and print it
    jsonified_output = json.dumps(output)

    with open("/shared/feedback.json", "w") as outfile:
            outfile.write(jsonified_output)
