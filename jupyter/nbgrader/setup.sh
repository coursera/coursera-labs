#!/bin/bash
mkdir -p ${JN_WORK_DIR}/.dotfiles-coursera
git config --global core.fileMode false

if [ -z "${WORKSPACE_TYPE}" ]
then
	# Launch grader
	$GRADER_FILES_PATH/grader.sh
else
	# Launch workspace
	cd $JN_WORK_DIR
	tini -- start-notebook.sh
fi
