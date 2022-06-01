#!/bin/bash
mkdir -p ${JN_WORK_DIR}/.dotfiles-coursera
git config --global core.fileMode false

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
	tini -- start-notebook.sh
fi
