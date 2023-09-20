#!/bin/bash

if [ "${WORKSPACE_TYPE}" = "student" ]
then
	# Delete grader files
	rm -rf $GRADER_FILES_PATH
	# Keep only validate extension for students
    jupyter nbextension disable --sys-prefix create_assignment/main
    jupyter nbextension disable --sys-prefix formgrader/main --section=tree
else 
	# enable custom formgrader extension
	jupyter serverextension enable --sys-prefix coursera.formgrader 
	# create nbgrader files for instructors if not exist
	cp -np $NBGRADER_FILES_PATH/.hidden $JN_WORK_DIR/.hidden
	cp -np $NBGRADER_FILES_PATH/nbgrader_config.py $JN_WORK_DIR/nbgrader_config.py
	mkdir -m 777 -p $JN_WORK_DIR/source
	mkdir -m 777 -p $JN_WORK_DIR/release
	cp -np $NBGRADER_FILES_PATH/release/nbgrader_config.py $JN_WORK_DIR/release/nbgrader_config.py
	cp -np $NBGRADER_FILES_PATH/release/options.json $JN_WORK_DIR/release/options.json
fi
