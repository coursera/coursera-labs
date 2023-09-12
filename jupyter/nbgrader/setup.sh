#!/bin/bash
mkdir -p ${JN_WORK_DIR}/.dotfiles-coursera
git config --global core.fileMode false

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
else
	# Launch workspace
	cd $JN_WORK_DIR
	tini -- jupyter lab --ip='*' --port=8888 --no-browser --allow-root
fi
