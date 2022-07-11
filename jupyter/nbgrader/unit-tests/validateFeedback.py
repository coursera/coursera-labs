import sys, re
from bs4 import BeautifulSoup

# This works by doing the following:
# 1. Make sure no HIDDEN TEST delimiters show up (confirm that tests are hidden in the cell input)
# 2. Check that the number hints displayed is correct
# 3. Check that the overall cell result is correct (which message shows up in cell output)

# Cell output messages based on overall cell result
CELL_PASSED_MESSAGE = "Congratulations! All test cases in this cell passed."
CELL_FAILED_MESSAGE = "One or more test cases in this cell did not pass."
CELL_ERROR_MESSAGE = "Total possible points in this cell was 0."

# Regex for the comment that determines the expected unit test behavior for each cell
EXPECTED_RESULTS = r'# Hidden Tests: (True|False), Expected Number of Hints: (\d+), Expected Result: (\w+)'

# Matches on the entire hint section
HINT_SECTION_REGEX = r'Instructor hints: \n(\t.*\n)+'
# Matches an individual hint
HINT_REGEX = r'\t.*\n'

# Matches the cell number
CELL_NUMBER_REGEX = r'<div class="prompt input_prompt">In\s+\[(\d+)\]:<\/div>'

# Result class to help store unit test results/feedback
class Result:
    def __init__(self):
        self.feedback = ""
        self.passed = True

# Read file into string
def get_feedback_text(file_path):
    with open(file_path, "r") as feedback_file:
        feedback_text = feedback_file.read()
        return feedback_text

# Search for HIDDEN TEST string that is part of hidden test pattern
# Returns true if no hidden tests are expected or if none are found
def check_for_hidden_tests(expected_hidden_tests, text, result):
    # If no hidden tests are expected, no further checks are needed
    if not expected_hidden_tests:
        return True
    
    # If they are expected, make sure HIDDEN TEST delimiter does not show up
    hidden_test_delimiter_match = re.search('HIDDEN TESTS', text) 
    if hidden_test_delimiter_match is not None:
        result.feedback += "Found hidden test delimiter.\n"
        return False

    # Lastly, check that we see "Hidden Tests Redacted" 
    test_redaction_str_match = re.search('Hidden Tests Redacted', text)
    if test_redaction_str_match is None:
        result.feedback += 'Did not find the "Hidden Tests Redacted" string.\n'
        return False
    else:
        return True

# Check that the cell has the correct number of hints
# Currently, we do not check the contents of the hints themselves
def check_for_hints(expected_num_hints, text, result):
    # Matches the whole section of hints
    hint_section = re.search(
        HINT_SECTION_REGEX,
        text
    )

    num_hints_found = 0
    if hint_section is not None:
        # Get the hints themselves.
        hint_section = hint_section.group()
        hints = re.findall(
            HINT_REGEX,
            hint_section
        )
        num_hints_found = len(hints)

    if expected_num_hints == num_hints_found:
        return True
    else:
        result.feedback += f'Found an unexpected number of comments. Expected {expected_num_hints}, found {num_hints_found}.\n'
        return False

# Check that the cell output contains the expected message
# If no message is expected, make sure output is empty
def check_cell_result(expected_cell_result, text, result):
    # Determine what output string we're searching for
    if expected_cell_result == 'pass': 
        cell_result_str = CELL_PASSED_MESSAGE
    elif expected_cell_result == 'fail':
        cell_result_str = CELL_FAILED_MESSAGE
    elif expected_cell_result == 'error':
        cell_result_str = CELL_ERROR_MESSAGE
    else:
        cell_result_str = ""

    if cell_result_str != "":
        # Search for the output string
        cell_result = re.search(
            cell_result_str,
            text
        )

        if cell_result is None:
            result.feedback += "Cell result output does not match what is expected.\n"
            return False
    else:
        # Search for the beginning of the output HTML
        cell_result = re.search(
            '<div class="output',
            text
        )

        if cell_result is not None:
            result.feedback += "Cell output should have been empty but is not.\n"
            return False

    return True

# Test a specific cell
def validate_cell(cell_text):
    result = Result()

    # Get cell number for identification purposes
    cell_num = re.search(
        CELL_NUMBER_REGEX,
        cell_text
    ).group(1)

    result.feedback += f"----------- Feedback for cell {cell_num} -----------\n"

    # Get the expected results for this particular cell
    expected_results = re.search(
        EXPECTED_RESULTS,
        cell_text
    )

    # Assign expected results
    if expected_results is not None: 
        expected_hidden_tests = expected_results.group(1) == "True" 
        expected_num_hints = int(expected_results.group(2))
        expected_cell_result = expected_results.group(3)
    else:
        # Default expected results if the expected results comment is not there
        expected_hidden_tests = False
        expected_num_hints = 0
        expected_cell_result = "None"

    # Check conditions surrounding hidden tests
    result.passed &= check_for_hidden_tests(expected_hidden_tests, cell_text, result)

    # Check for the correct number of hints
    result.passed &= check_for_hints(expected_num_hints, cell_text, result)

    # Check the result of the cell
    result.passed &= check_cell_result(expected_cell_result, cell_text, result)

    if not result.passed:
        print(result.feedback)
        return 0
    else:
        return 1

# Driver method that takes the file, parses it, and runs the cell-by-cell tests
def validate_feedback(file_path):
    feedback_text = get_feedback_text(file_path)
    S = BeautifulSoup(feedback_text, 'lxml')

    # This gets a list of code cells
    cells = S.find_all(class_= 'cell border-box-sizing code_cell rendered')

    passed_cells = 0

    # Go through cell by cell validating each one's contents
    for cell in cells:
        passed_cells += validate_cell(str(cell))

    if passed_cells == len(cells):
        print("All cells passed validation!")
    else:
        print(f"{passed_cells} out of {len(cells)} passed.")

if __name__ == "__main__": 
    if len(sys.argv) != 2:
        print("Invalid number of arguments provided")
        exit(1)

    path_to_feedback_file = sys.argv[1]

    print(f"Running validation tests on {path_to_feedback_file}...")

    validate_feedback(path_to_feedback_file)