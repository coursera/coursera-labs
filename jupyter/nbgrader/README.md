# Coursera Nbgrader Images

Coursera labs nbgrader images are pulled onto both labs and grid platform. The same image is used for learners to solve jupyter notebook assignment and autograde learner assignments. 

More details about the image can be found [here](https://docs.google.com/document/d/1cSTD7RaxJhb4HxLTuZsnU9oLoM15JK0QJl3PEzPn5to#heading=h.5gnwgc5i6964)

## Base Images

### Scipy Image 
`docker build -t scipy-notebook-v2.0-nbgrader:latest --build-arg BASE_IMAGE_NAME=jupyter/scipy-notebook --build-arg BASE_IMAGE_TAG=3b1f4f5e6cc1 .`

### Datascience Image
`docker build -t datascience-notebook-v2.0-nbgrader:latest --build-arg BASE_IMAGE_NAME=jupyter/datascience-notebook --build-arg BASE_IMAGE_TAG=3b1f4f5e6cc1 .`

### Tensorflow Image
`docker build -t tensorflow-notebook-v2.0-nbgrader:latest --build-arg BASE_IMAGE_NAME=jupyter/tensorflow-notebook --build-arg BASE_IMAGE_TAG=3b1f4f5e6cc1 .`

## How Hidden Feedback Works
Recap of how we hide nbgrader generated feedback. This does not mention anything about `setup.sh` or `nbgrader-setup.sh` or `preamble.html`; this explains what happens in `scrub.py`.

1. `nbgrader generate_feedback` generates an HTML file with a summary of the assignment results and also a view of every cell and its execution output.

2. `scrub.py` is called, taking in the feedback file, maximum score, and kernel language.

3. We check that we have the expected number of arguments and load in `options.json` if it exists.

4. `get_processed_feedback` will replace all hidden tests and hidden feedback with the redaction strings specified in `options.json` and modify styling for accessibility. It does this by breaking the original HTML into chunks per cell.

    i. We search for the presence of the `HIDDEN TEST` delimiters in each cell's input area. If we don't find it, then we don't need to do any redaction, so we just return. Otherwise, we redact feedback based on the notebook's kernel language. For Python and R, we also want to redact anything printed to stdout/stderr so that students can't use print statements to get the assignment inputs. 

        - Python: Redaction is done based on HTML classes. Unhidden tests will be redacted if they occur after a hidden test.

        - R: The generated output for R is just a bunch of text. We keep the first line, which includes the test description, and redact everything else.

        - Julia: This one is tricky, because the feedback formatting is not consistent (sometimes it'll be one big div, other times it's split haphazardly between a bunch of divs). We basically take the required information to recreate the last test summary table in the output, redact everything else, and then reconstruct the table. 

    ii. We intensify colors (add `-intense` to their classes) and also make some slight color adjustments to make sure we have sufficient color contrast.

    iii. Fix `top` hyperlink within the cells so they actually bring you to the top.

5. Update the scores within each cell so that they are scaled up to the coursera maximum score for the assignment.

6. Append `preamble.html` so that we get the summary in the left panel.