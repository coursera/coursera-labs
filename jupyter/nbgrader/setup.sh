#!/bin/bash
mkdir -p ${JN_WORK_DIR}/.dotfiles-coursera
git config --global core.fileMode false
$NBGRADER_FILES_PATH/nbgrader-setup.sh

if [ "${WORKSPACE_TYPE}" = "student" ]; then
    jupyter labextension disable --level=sys_prefix nbgrader/assignment-list && \
    jupyter labextension disable --level=sys_prefix nbgrader/formgrader && \
    jupyter labextension disable --level=sys_prefix nbgrader/create-assignment && \
    jupyter labextension disable --level=sys_prefix nbgrader/course-list && \
    jupyter serverextension disable --sys-prefix nbgrader.server_extensions.assignment_list && \
    jupyter serverextension disable --sys-prefix nbgrader.server_extensions.course_list && \
    jupyter serverextension disable --sys-prefix nbgrader.server_extensions.formgrader
fi
if [ -z "${WORKSPACE_TYPE}" ]
then
	# Launch grader
	$GRADER_FILES_PATH/grader.sh
elif [ "${WORKSPACE_TYPE}" = "test" ]
then
	# Run unit tests
	$UNIT_TEST_FILES_PATH/setupUnitTests.sh
	$UNIT_TEST_FILES_PATH/runUnitTests.sh python
	$UNIT_TEST_FILES_PATH/runUnitTests.sh julia
	$UNIT_TEST_FILES_PATH/runUnitTests.sh r


	# Clean up
	rm -rf unit-test-env
else
	# Launch workspace
	cd $JN_WORK_DIR
	echo "Launching workspace"
	tini -- jupyter lab --ip='*' --port=8888 --no-browser --allow-root
fi
