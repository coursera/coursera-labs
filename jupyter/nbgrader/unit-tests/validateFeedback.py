import sys, re
from bs4 import BeautifulSoup

# This works by checking the following:
# 1. Make sure no HIDDEN TEST delimiters show up (confirm that tests are hidden in the cell bodies)
# 2. Check that the number of tests hidden is correct
# 3. For cells that feature hidden tests, check that traceback is redacted if present

NUM_HIDDEN_TESTS = 8

def get_feedback_text(file_path):
    with open(file_path, "r") as feedback_file:
        feedback_text = feedback_file.read()
        return feedback_text

def check_for_hidden_test_string(text):
    return re.search(
        'HIDDEN TESTS',
        text
    )

def check_hidden_test_occurrences(text):
    return len(re.findall(
        'Test Hidden',
        text
    ))

def check_traceback_redaction(cell):
    # If there's no "Test hidden" in the prompt box, then no redaction/checking is needed for this cell
    if (check_hidden_test_occurrences(cell) == 0):
        return

    # If "traceback" is present, then "traceback redacted must also be present"
    traceback_present = re.search(
        'Traceback',
        cell
    )

    # If traceback is not present, then no redaction is necessary
    if traceback_present == None:
        print("no traceback found")
    else:
        assert re.search('Traceback Redacted', cell) != None, "Some traceback was not redacted."

def validate_redaction(file_path):
    feedback_text = get_feedback_text(file_path)
    S = BeautifulSoup(feedback_text, 'lxml')

    # This gets a list of code cells
    divs = S.find_all(class_= 'cell border-box-sizing code_cell rendered')

    assert None == check_for_hidden_test_string(feedback_text), "HIDDEN TESTS string found"
    assert NUM_HIDDEN_TESTS == check_hidden_test_occurrences(feedback_text), "Incorrect number of tests hidden"
    for cell in divs:
        check_traceback_redaction(cell.text)

if __name__ == "__main__": 
    if len(sys.argv) != 2:
        print("Invalid number of arguments provided")
        exit(1)

    path_to_feedback_file = sys.argv[1]

    validate_redaction(path_to_feedback_file)

    print("All tests pass!")