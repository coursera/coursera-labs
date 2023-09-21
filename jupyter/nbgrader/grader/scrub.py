# 07-12-2021: Blake Johnson
# 09-28-2021: Joseph Li
import os,re,json,sys

from scoreCalculator import scoreCalculator

from bs4 import BeautifulSoup

import logging

# Regular Expressions for HTML to get redacted

# Matches HTML that signifies the beginning and end of HIDDEN TESTS
HIDDEN_TEST_REGEX = r'<span class=".*?">###\s*BEGIN HIDDEN TESTS\s*<\/span>[\w\W]*?<span class=".*?">###\s*END HIDDEN TESTS\s*<\/span>'

# Matches on "Score: {num} / {den}"
SCORE_REGEX = r'Score:\s*(\d+(?:.\d+)?)\s*/\s*(\d+(?:.\d+)?)'

# Matches on <a name="{cell_name}">
NAME_REGEX = r'<a name="(.*?)">'

# Matches on <div class="prompt input_prompt">In [{num}]:</div>
CELL_NUM_REGEX = re.compile(r"\[(\d+)\]")

# Nbgrader cells (input and output pair) all begin with 
# `<div class="cell border-box-sizing code_cell rendered">`
# The lookahead will match the next cell or the end of the body tag (using 
# capture groups here would involve adding a lot of unreadable complexity to
# accurately find the correct matching end tag).
# By using look-behind and look-ahead, we get the contents of the cell itself.
CELL_BORDER_REGEX = r'(?s)<div class="cell border-box-sizing code_cell rendered">(.*?)<\/div>\s*<\/div>\s*<\/div>\s*<\/div>\s*<\/div>\s*<\/div>\s*<\/div>'

# Matches on the HTML that wraps an entire output section. 
# We don't technically need to specify all of the opening tags, but they are
# here to provide some context for the closing tags.
CELL_OUTPUT_REGEX = r'<div class="output_wrapper">\s*<div class="output">\s*<div class="output_area">\s*<div class="prompt.*?">.*?</div>\s*<div class=".*?output_subarea.*?">[\w\W]*?</div>\s*</div>\s*</div>\s*</div>'

# Matches on the HTML for a single line hint in the cell input section.
STRING_REGEX = r'<span class="s\d*">([\w\W]+?)</span>'

R_TEST_FUNCTIONS = ["test_that", "stop"]
R_TEST_FUNCTIONS_STRING = '|'.join(R_TEST_FUNCTIONS)

# We need the surrounding context because span class="s" is a generic class for strings
R_HINT_REGEX = rf'<span class="nf">(?:{R_TEST_FUNCTIONS_STRING})</span>\s*<span class="p">\(</span>[\w\W]*?{STRING_REGEX}\s*'

PYTHON_NOT_IMPLEMENTED_REGEX = rf'<span class="ansi-red-fg">NotImplementedError</span>'
R_NOT_IMPLEMENTED_REGEX = rf'.NotYetImplemented()'
JULIA_NOT_IMPLEMENTED_REGEX = rf'Not Yet Implemented'

CELL_PASSED_MESSAGE = "<span style='color: green; font-weight: bold;'>Congratulations! All test cases in this cell passed.</span>\n"
CELL_FAILED_MESSAGE = "<span style='color: red; font-weight: bold;'>One or more test cases in this cell did not pass.</span>\n"
CELL_ERROR_MESSAGE = "<span style='color: black; font-weight: bold;>Total possible points in this cell was 0.</span>\n"

# Get the path for the clean file
def get_clean_path(file_path):
	clean_path = file_path + '.clean'
	return clean_path

# Get the original feedback text
def get_feedback_text(file_path):
	with open(file_path, "r") as orig_file:
		orig_text = orig_file.read()
		return orig_text

# Turn output string into nbgrader-generated styled HTML string.
# This is done by repeatedly applying divs until the overall string matches
# the tags and style of an nbgrader-generated output section.
def stylize_output(message):
	if message != "":
		message = f"""
			<div class='output_wrapper'>
				<div class='output'>
					<div class='output_area'>
						<div class='prompt'></div>
						<div class='output_subarea output_stream output_stdout output_text'>
							<pre>{message}</pre>
						</div>
					</div>
				</div>
			</div>
		"""
	return message

def extract_cell_name(soup):
    cell_name_element = soup.find('a')
    return cell_name_element.get('name') if cell_name_element else None

def extract_cell_number(soup):
    input_prompt = soup.find("div", class_="prompt input_prompt")
    matched_number = CELL_NUM_REGEX.search(input_prompt.string)
    cell_number = int(matched_number.group(1)) if matched_number else None

    if not matched_number:
        logging.warning("Cell number search unsuccessful")

    return cell_number

def extract_score(cell_html):
	cell_score = re.search(
		SCORE_REGEX,
		cell_html
	)
	return cell_score

def extract_hints(soup, kernel_language, cell_html):
	if kernel_language == "R":
		hint_regex = R_HINT_REGEX
		hints = re.findall(
			hint_regex,
			cell_html,
		)
	elif kernel_language == "julia":
		hints = []
		testset_tags = soup.select("span:contains('@testset')")

		# Iterate through the '@testset' elements
		for tag in testset_tags:

			sibling = tag.find_next_sibling()

			# Iterate through the siblings until a 'span' containing 'begin' is encountered
			while sibling and not (sibling.name == 'span' and sibling.has_attr('class') and 'k' in sibling['class'] and sibling.get_text(strip=True) == 'begin'):
				# Check if the sibling element matches 'span[class*=s]'
				if sibling.name == 'span' and sibling.has_attr('class') and any('s' in c for c in sibling['class']):
					hints.append(sibling.get_text(strip=True).strip('\'"'))

				sibling = sibling.find_next_sibling()
	else:  # Python
		hint_elems = soup.select("span.k:contains(assert) ~ span.p:contains(',') + span[class*=s]")
		hints = [elem.get_text(strip=True).strip('\'"') for elem in hint_elems]
	return hints

def extract_not_implemented(cell_html, kernel_language):
	if kernel_language == "R":
		not_implemented_regex = R_NOT_IMPLEMENTED_REGEX
	elif kernel_language == "julia":
		not_implemented_regex = JULIA_NOT_IMPLEMENTED_REGEX
	else:  # Python
		not_implemented_regex = PYTHON_NOT_IMPLEMENTED_REGEX
	
	is_not_implemented = re.search(
		not_implemented_regex,
		cell_html
	)
	return is_not_implemented

def construct_output_message(output, testCaseResults, cell_name, cell_score, hints, cell_number, is_not_implemented):
	if cell_score is not None:

		testCaseResult = {
			"testName": cell_name,
			"result": "ERROR",
		}
		cell_score_numerator = float(cell_score.group(1))
		cell_score_denominator = float(cell_score.group(2))

		# Construct the output message
		if cell_score_denominator == 0:
			output += CELL_ERROR_MESSAGE
		elif cell_score_numerator == cell_score_denominator:
			output += CELL_PASSED_MESSAGE
			testCaseResult["result"] = "PASS"
		else:
			output += CELL_FAILED_MESSAGE
			if len(hints) > 0:
				output += "Instructor hints: \n"
			count = 1
			for hint in hints:
				output += f"\t{count}. {hint}\n"
				count += 1

			testCaseResult["result"] = "SKIP" if is_not_implemented else "FAIL"
		testCaseResult["testIndex"] = cell_number
		testCaseResults.append(testCaseResult)

		# Stylize output
		output = stylize_output(output)
	return output

# Method to handle all of the feedback processing
def redact_feedback(cell_html, options, kernel_language, testCaseResults):
	cell_html = ''.join(str(item) for item in cell_html)
	soup = BeautifulSoup(cell_html, 'html.parser')

	# Process cell traceback only if option is set. Not having this set will leave assignment vulnerable to notebook dump
	if options['hideTraceback']:
		# Initialize the output string builder
		output = ""

		# Get cell name, score and number
		cell_name = extract_cell_name(soup)
		cell_score = extract_score(cell_html)
		cell_number = extract_cell_number(soup)

		# Check whether we see any "Not Implemented" error to determine whether the student attempted this cell
		is_not_implemented = extract_not_implemented(cell_html, kernel_language)
		# Look for instructor hints
		hints = extract_hints(soup, kernel_language, cell_html)
		
		# Construct the output message
		output = construct_output_message(output, testCaseResults, cell_name, cell_score, hints, cell_number, is_not_implemented)

		# Remove all generated output so we can use our own
		cell_html = re.sub(
			CELL_OUTPUT_REGEX,
			"",
			cell_html
		)
		# Add our now stylized output to the HTML document
		cell_html += output

	# Remove hidden tests
	if options['hideHiddenTests']:
		cell_html = re.sub(
			HIDDEN_TEST_REGEX,
			'<span>' + options['hiddenTestText'] + '</span>',
			cell_html,
		)
	# Create a BeautifulSoup object from the new content
	redacted_soup = BeautifulSoup(cell_html, 'html.parser')

	# Cell align
	# input_prompt = new_soup.find('div', class_='prompt input_prompt')
	# input_prompt['style'] = 'display: inline-block; width: 5%; vertical-align: top;'

	create_cell_wrapper_div(redacted_soup)
	return redacted_soup
# Add -intense class to colors to increase contrast
def intensify_colors(match):

	# cyan-intense is not enough, switch cyan to blue
	color_prefix = re.sub(
		r'cyan',
		'blue',
		match.group(),
	)

	# white-intense is not enough, switch white to black
	color_prefix = re.sub(
		r'white',
		'black',
		color_prefix,
	)

	# only add -intense suffix if not already present
	is_intense = re.search(
		r'-intense',
		color_prefix
	)
	if is_intense is None:
		color_prefix = color_prefix + '-intense'

	return color_prefix

# Color adjustments to have contrast > 4.5:1
def fix_contrast(contrasted_feedback):

	# intensify colors to increase contrast
	contrasted_feedback = re.sub(
		r'(?<=<span class=)"ansi-\w*?(-intense)?(?=-fg)',
		intensify_colors,
		contrasted_feedback,
	)

	# Change color of "top" hyperlinks to black for contrast
	contrasted_feedback = re.sub(
		r'<a href="#top">\(Top\)</a>',
		'<a href="#top" style="color: black">(Top)</a>',
		contrasted_feedback,
	)

	# change some css styling to meet contrast accessibility threshold
	contrasted_feedback = re.sub(
		r'[dD]84315',
		'c84315',
		contrasted_feedback
	)
	contrasted_feedback = re.sub(
		r'[aA]{2}22[fF]{2}',
		'aa12ff',
		contrasted_feedback
	)

	return contrasted_feedback

def round_numbers_in_fraction(match):
    num1, num2 = map(float, (match.group(1), match.group(2)))
    return f"{round(num1)} / {round(num2)}"

# Remove hidden tests and traceback from feedback html
def get_processed_feedback(processed_feedback, options, kernel_language):
	testCaseResults = []
	soup = BeautifulSoup(processed_feedback, 'html.parser')

	# Breaks HTML in chunks per cell
	elements = soup.find_all('div', class_='cell border-box-sizing code_cell rendered')
	for element in elements:
		new_soup = redact_feedback(element.contents, options, kernel_language, testCaseResults)
		element.replace_with(new_soup)

	# Puts cell elements inside cell_wrapper to align cell numbers with Jupyter Lab format
	soup = apply_cell_wrappers(soup)
	redacted_feedback = str(soup)

	# Get above accessibility contrast threshold
	redacted_feedback = fix_contrast(redacted_feedback)

	# Fix "top" hyperlink destination
	redacted_feedback = re.sub(
		r'<a name="top"></a>',
		'',
		redacted_feedback,
	)
	redacted_feedback = re.sub(
		r'(?=<div class="container" id="notebook-container">)',
		'<a name="top"></a>',
		redacted_feedback,
	)

	return redacted_feedback, testCaseResults

# Nbgrader generates a score / total for all individual test cells as well as one for 
# the overall assignment. We use this to get the total nbgrader points possible from
# the assignment by keeping the max value that shows up in the denominators of strings
# matching the regex "Score: score / total".
def get_total_points(score_iter):
	total_points = -1

	for match in score_iter:
		points_poss = float(match.group(1))

		if (points_poss > total_points):
			total_points = points_poss
	
	return total_points

# Scale up the individual cell scores based on coursera max score for the assignment
def update_score(score_match, multiplier):
	points_rec = float(score_match.group(1))
	points_poss = float(score_match.group(2))

	adj_points_rec = round(points_rec * multiplier, 2)
	adj_points_poss = round(points_poss * multiplier, 2)

	adjusted_score = "{}{} / {}".format("Score: ", adj_points_rec, adj_points_poss)
	return adjusted_score

# Update nbgrader score to match overall Coursera score
def get_updated_score(clean_feedback, max_score):
	clean_text = clean_feedback

	# Set total points possible
	score_iter = re.finditer(
		SCORE_REGEX,
		clean_feedback
	)

	total_points = get_total_points(score_iter)

	# get score multiplier to scale up to maximum coursera score
	multiplier = float(max_score) / float(total_points) if total_points != 0 else 0

	# Update cell points
	# Need to use lambda in order to pass arguments into the repl function
	clean_text = re.sub(
		SCORE_REGEX,
		lambda match: update_score(match, multiplier),
		clean_text
	)

	return clean_text

## TESTING
def print_elements_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for name in files:
            print(os.path.join(root, name))
        for name in dirs:
            print(os.path.join(root, name))

def round_numbers_in_fraction(match):
	print("FOUND MATCH: ", match)
	num1, num2 = map(float, (match.group(1), match.group(2)))
	return f"{round(num1)} / {round(num2)}"

def create_cell_wrapper_div(soup):
	# Get the input and output elements
	input = soup.find('div', class_='input')
	output = soup.find('div', class_='output_wrapper')

	# Create a new wrapping div
	input_output_div = soup.new_tag('div')
	input_output_div['class'] = 'cell border-box-sizing code_cell rendered'
	
	#Inserts wrapper div directly before the input element in the DOM tree 
	input.insert_before(input_output_div)

	# Append the target elements to the new wrapping div
	if input:
		input_output_div.append(input.extract())
	if output: 
		input_output_div.append(output.extract())
	return soup

def wrap_cell_elements(soup, cell):
    # Locate the input_prompt div
    input_prompt = cell.find('div', class_='input_prompt')

    # Create a new wrapper div
    wrapper_div = soup.new_tag('div')
    wrapper_div['class'] = 'cell_wrapper'

    # Insert wrapper div before the input_prompt div in the DOM tree
    cell.insert_before(wrapper_div)
    wrapper_div.append(cell)

    # Find the input_prompt and nbgrader_cell divs
    input_prompt = cell.find('div', class_='prompt input_prompt')

    # Extract the input_prompt div
    input_prompt.extract()

    # Insert the input_prompt div before the nbgrader_cell div
    cell.insert_before(input_prompt)


def apply_cell_wrappers(soup):

    # Iterate through all 'cell border-box-sizing code_cell rendered' elements and wrap them in .cell_wrapper
    cells = soup.find_all('div', class_='cell border-box-sizing code_cell rendered')
    for cell in cells:
        wrap_cell_elements(soup, cell)

    # Find all style tags
    style_tags = soup.find_all('style')

    # Initialize the target style_tag
    target_style_tag = None

    # Iterate through all style tags to find the one containing 'div.prompt'
	# Needed to overwrite nbgrader defaults 
    for style_tag in style_tags:
        start = style_tag.string.find('div.prompt')
        if start != -1:
            target_style_tag = style_tag
            break

    if target_style_tag is not None:
        # Find the positions of div.prompt rule in the target_style_tag
        start = target_style_tag.string.find('div.prompt')
        end = target_style_tag.string.find('}', start)

        # Split at the target rule
        first_part = target_style_tag.string[:start]
        second_part = target_style_tag.string[end + 1:]

        style_content = '''
        .cell_wrapper {
            display: flex;
            align-items: flex-start;
        }

        .input_prompt {
            white-space: nowrap;
            min-width: fit-content;
            margin-right: 1em;
        }

        .border-box-sizing.code_cell.rendered {
            width: 90%;
        }
        '''

        # Remove the triple quotes and rebuild the style tag content
        target_style_tag.string = first_part + style_content.strip() + second_part
    else:
        logging.warning("div.prompt not found in any style tags, nbgrader styling may have changed")
    return soup

# Create a clean feedback version of a file
def clean_feedback(
	nbgrader_learner, assignment_name, decoded_feedback, notebook_filename, options, kernel_language, max_score):
	# Construct file path
	file_path = f"feedback/{nbgrader_learner}/{assignment_name}/{decoded_feedback}"

	clean_path = get_clean_path(file_path)

	# Get the original text then process it
	print_elements_in_directory('feedback/courseraLearner/')
	orig_text = get_feedback_text(file_path)
	(clean_feedback, testCaseResults) = get_processed_feedback(orig_text, options, kernel_language)
	clean_text = get_updated_score(clean_feedback, max_score)

	# Get the preamble text
	preamble_text = ""
	with open("preamble.html", "r") as preamble_file:
		preamble_text = preamble_file.read() 
		
	# Add the preamble to the cleaned feedback
	clean_text = preamble_text + clean_text

	# Add the max score to the feedback
	score_input = f"<input type=\"hidden\" id=\"maxscore-var\" value=\"{max_score}\" />"
	clean_text = re.sub(
		r"<body>",
		f"<body>{score_input}",
		clean_text
	)

	# Write the new cleaned file
	with open(clean_path, "w") as clean_file:
		clean_file.write(clean_text)

	scoreCalculator(assignment_name, notebook_filename, nbgrader_learner, testCaseResults)

# Process all the files
if __name__ == "__main__":
	if len(sys.argv) < 7:
		print("Invalid number of arguments provided")
		exit(1)

	# username for the learner
	nbgrader_learner = sys.argv[1]
	# the name of the assignment (folder) in nbgrader formgrader
	assignment_name = sys.argv[2]
	# .html feedback file for the assignment
	decoded_feedback = sys.argv[3]
	# maximum score for the corresponding part (set on Coursera platform)
	coursera_part_max_score = sys.argv[4]
	# language of the Jupyter notebook kernel
	kernel_language_raw = sys.argv[5]
	# .ipynb file of the assignment
	notebook_filename = sys.argv[6]

	# Load the options file
	options = {}
	if os.path.isfile("/shared/grader/options.json"):
		with open("/shared/grader/options.json") as f:
			options = json.load(f)
	else:
		options = {
			"hideHiddenTests": True,
			"hiddenTestText": "Hidden Tests Redacted",
			"hideTraceback": True,
			"hiddenTracebackText": "Traceback Redacted"
		}
	kernel_language = kernel_language_raw.strip('"')

	clean_feedback(
		nbgrader_learner, 
		assignment_name, 
		decoded_feedback, 
		notebook_filename, 
		options, 
		kernel_language, 
		coursera_part_max_score
		)
