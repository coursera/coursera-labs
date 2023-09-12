# The default script for cleaning up Nbgrader feedback files
# 07-12-2021: Blake Johnson
# 09-28-2021: Joseph Li
import os,re,json,sys

from scoreCalculator import scoreCalculator

from bs4 import BeautifulSoup

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
CELL_BORDER_REGEX = r'(?<=<div class="cell border-box-sizing code_cell rendered">)[\w\W]*?(?=(</div>\s*<div class="cell )|(</div>\s*){6}</body>)'

# Matches on the HTML that wraps an entire output section. 
# We don't technically need to specify all of the opening tags, but they are
# here to provide some context for the closing tags.
CELL_OUTPUT_REGEX = r'<div class="output_wrapper">\s*<div class="output">\s*<div class="output_area">\s*<div class="prompt.*?">.*?</div>\s*<div class=".*?output_subarea.*?">[\w\W]*?</div>\s*</div>\s*</div>\s*</div>'

# Matches on the HTML for a single line hint in the cell input section.
STRING_REGEX = r'<span class="s\d*">([\w\W]+?)</span>'

R_TEST_FUNCTIONS = ["test_that", "stop"]
R_TEST_FUNCTIONS_STRING = '|'.join(R_TEST_FUNCTIONS)

# We need the surrounding context because span class="s" is a generic class for strings
PYTHON_HINT_REGEX = rf'<span class="k">assert[\w\W]+?<span class="p">.*?,</span>\s*{STRING_REGEX}'
R_HINT_REGEX = rf'<span class="nf">(?:{R_TEST_FUNCTIONS_STRING})</span>\s*<span class="p">\(</span>[\w\W]*?{STRING_REGEX}\s*'
JULIA_HINT_REGEX = rf'<span class="nd">@testset</span>\s*{STRING_REGEX}\s*<span class="k">begin</span>'

PYTHON_NOT_IMPLEMENTED_REGEX = rf'<span class="ansi-red-fg">NotImplementedError</span>'
R_NOT_IMPLEMENTED_REGEX = rf'.NotYetImplemented()'
JULIA_NOT_IMPLEMENTED_REGEX = rf'Not Yet Implemented'

CELL_PASSED_MESSAGE = "<span class='ansi-green-intense-fg ansi-bold'>Congratulations! All test cases in this cell passed.</span>\n"
CELL_FAILED_MESSAGE = "<span class='ansi-red-intense-fg ansi-bold'>One or more test cases in this cell did not pass.</span>\n"
CELL_ERROR_MESSAGE = "<span class='ansi-black-fg ansi-bold'>Total possible points in this cell was 0.</span>\n"

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

# Method to handle all of the feedback processing
def redact_feedback(match_obj, options, kernel_language, testCaseResults):
	# print("Match: ", match_obj)
	if kernel_language == "R":
		hint_regex = R_HINT_REGEX
		not_implemented_regex = R_NOT_IMPLEMENTED_REGEX
	elif kernel_language == "julia":
		hint_regex = JULIA_HINT_REGEX
		not_implemented_regex = JULIA_NOT_IMPLEMENTED_REGEX
	else:
		hint_regex = PYTHON_HINT_REGEX
		not_implemented_regex = PYTHON_NOT_IMPLEMENTED_REGEX

	cell_html = match_obj.group()
	soup = BeautifulSoup(cell_html, 'html.parser')

	# Process cell traceback only if option is set. Not having this set will leave assignment vulnerable to notebook dump
	if options['hideTraceback']:
		# print("Cell HTML: ", cell_html)
		# Initialize the output string builder
		output = ""

		cell_name = re.search(
			NAME_REGEX,
			cell_html
		)
		print("Cell Name: ", cell_name)

		# Get score
		cell_score = re.search(
			SCORE_REGEX,
			cell_html
		)
		print("Cell Score:", cell_score)

		# Check whether we see any "Not Implemented" error to determine whether the student attempted this cell
		is_not_implemented = re.search(
			not_implemented_regex,
			cell_html
		)
		print("Not impletemented: ", is_not_implemented)

		# Look for instructor hints
		hints = re.findall(
			hint_regex,
			cell_html,
		)		
		print("Hints: ", hints)

		# Get cell number
		input_prompt = soup.find("div", class_="prompt input_prompt")
		matched_number = CELL_NUM_REGEX.search(input_prompt.string)

		#Testing
		if matched_number:
			cell_number = int(matched_number.group(1))
			print(f"Cell number: {cell_number}")
		else:
			print("No cell number found")

		# Use score to check whether all test cases passed
		if cell_score is not None:
			testCaseResult = {
				"testName": cell_name.group(1),
				"result": "ERROR",
			}
			print("Test Case Res", testCaseResult)
			cell_score_numerator = float(cell_score.group(1))
			cell_score_denominator = float(cell_score.group(2))
			print(f"{cell_score_denominator} / {cell_score_denominator}")
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

				testCaseResult["result"] = "NO_ATTEMPT" if is_not_implemented else "FAIL"
			testCaseResult["testIndex"] = matched_number
			testCaseResults.append(testCaseResult)
			
			# Stylize output
			output = stylize_output(output)

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

	return cell_html

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

# Remove hidden tests and traceback from feedback html
def get_processed_feedback(processed_feedback, options, kernel_language):
	testCaseResults = []

	# Breaks HTML in chunks per cell
	redacted_feedback = re.sub(
		CELL_BORDER_REGEX,
		lambda match: redact_feedback(match, options, kernel_language, testCaseResults),
		processed_feedback,
	)
	# print("Redacted feedback: ", redacted_feedback)
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

# Create a clean feedback version of a file
def clean_feedback(
	nbgrader_learner, assignment_name, decoded_feedback, notebook_filename, options, kernel_language, max_score):
	# Construct file path
	file_path = f"feedback/{nbgrader_learner}/{assignment_name}/{decoded_feedback}"

	clean_path = get_clean_path(file_path)

	# Get the original text then process it
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

	print("Args: ", sys.argv)
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
	print("Max Score: ", coursera_part_max_score)
	clean_feedback(
		nbgrader_learner, 
		assignment_name, 
		decoded_feedback, 
		notebook_filename, 
		options, 
		kernel_language, 
		coursera_part_max_score)
