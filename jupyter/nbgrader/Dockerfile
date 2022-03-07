# Jupyter Notebook images with Nbgrader
# Requirements:
#   Argument BASE_IMAGE_NAME must be a valid Jupyter Notebook docker image
#
# Options:
#   Argument BASE_IMAGE_TAG may select a version other than latest

ARG BASE_IMAGE_NAME=jupyter/datascience-notebook
ARG BASE_IMAGE_TAG=3b1f4f5e6cc1
FROM ${BASE_IMAGE_NAME}:${BASE_IMAGE_TAG}

ENV NBGRADER_FILES_PATH=/coursera/nbgrader-files
ENV GRADER_FILES_PATH=/coursera/grader
ENV JN_WORK_DIR=/home/$NB_USER/work

# Install nbgrader
RUN pip install nbgrader==0.6.1

USER root
RUN mkdir -p $GRADER_FILES_PATH
RUN mkdir -p $NBGRADER_FILES_PATH

# Add nbgrader files
COPY nbgrader-files/nbgrader-setup.sh /usr/local/bin/start-notebook.d/nbgrader-setup.sh
COPY nbgrader-files/ $NBGRADER_FILES_PATH
RUN chmod 777 -R $NBGRADER_FILES_PATH/
# Add grid files
COPY grader/ $GRADER_FILES_PATH

COPY setup.sh /coursera/setup.sh
RUN chmod 777 -R /coursera

# Add submit button, copy for each version of python in the kernel
COPY ./jupyter-extension/coursera /tmp/coursera
RUN for d in $(ls $CONDA_DIR/lib | grep "^python*") ; do cp -r /tmp/coursera $CONDA_DIR/lib/$d; done

COPY ./jupyter-extension/nbextensions/submit-button $CONDA_DIR/jupyter-extension/jupyter/nbextensions/submit-button
RUN jupyter nbextension install $CONDA_DIR/jupyter-extension/jupyter/nbextensions/submit-button && \
    jupyter nbextension enable submit-button/main

COPY ./jupyter-extension/.jupyter/ /home/$NB_USER/.jupyter/
RUN fix-permissions /home/$NB_USER/.jupyter
ENV PYTHONWARNINGS ignore

# Need to run as root for grader to write into /shared/feedback.json
# we have user namespaces enabled
#USER $NB_USER

# Enable all nbgrader extensions
RUN jupyter nbextension install --sys-prefix --py nbgrader --overwrite && \
    jupyter nbextension enable --sys-prefix --py nbgrader && \
    jupyter serverextension enable --sys-prefix --py nbgrader
# Disable Assignment List and Course List extensions for everyone
RUN jupyter nbextension disable --sys-prefix assignment_list/main --section=tree && \
 	jupyter serverextension disable --sys-prefix nbgrader.server_extensions.assignment_list && \
 	jupyter nbextension disable --sys-prefix course_list/main --section=tree && \
 	jupyter serverextension disable --sys-prefix nbgrader.server_extensions.course_list && \
 	# Disable official formgrader server extension
 	jupyter serverextension disable --sys-prefix nbgrader.server_extensions.formgrader

# Persist git configuration options
RUN ln -s /home/$NB_USER/work/.dotfiles-coursera/.gitconfig /home/$NB_USER/.gitconfig
RUN ln -s /home/$NB_USER/work/.dotfiles-coursera/.git-credentials /home/$NB_USER/.git-credentials

VOLUME /shared

RUN fix-permissions /home/jovyan/.jupyter

ENTRYPOINT ["/coursera/setup.sh"]
