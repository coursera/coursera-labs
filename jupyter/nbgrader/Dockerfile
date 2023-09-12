# Jupyter Notebook images with Nbgrader
# Requirements:
#   Argument BASE_IMAGE_NAME must be a valid Jupyter Notebook docker image
#
# Options:
#   Argument BASE_IMAGE_TAG may select a version other than latest

ARG BASE_IMAGE_NAME=jupyter/datascience-notebook
ARG BASE_IMAGE_TAG=latest
FROM ${BASE_IMAGE_NAME}:${BASE_IMAGE_TAG}

ENV NBGRADER_FILES_PATH=/coursera/nbgrader-files
ENV GRADER_FILES_PATH=/coursera/grader
ENV UNIT_TEST_FILES_PATH=/coursera/unit-tests
ENV JN_WORK_DIR=/home/$NB_USER/work
ENV NLTK_DATA=/home/$NB_USER/work/nltk_data

# Install nbgrader
RUN pip install -U "jupyterlab<3.6" nbgrader lxml

USER root
RUN mkdir -p $GRADER_FILES_PATH
RUN mkdir -p $NBGRADER_FILES_PATH

# Add nbgrader files
COPY nbgrader-files/nbgrader-setup.sh /usr/local/bin/start-notebook.d/nbgrader-setup.sh
COPY nbgrader-files/ $NBGRADER_FILES_PATH
RUN chmod 777 -R $NBGRADER_FILES_PATH/
COPY setup.sh /coursera/setup.sh
RUN chmod 777 -R /coursera
RUN mkdir -p /usr/local/share/nbgrader/exchange && chmod 777 /usr/local/share/nbgrader/exchange

# Add grid files
COPY grader/ $GRADER_FILES_PATH

# Add submit button, copy for each version of python in the kernel
COPY ./jupyter-extension/coursera /tmp/coursera
RUN for d in $(ls $CONDA_DIR/lib | grep "^python*") ; do cp -r /tmp/coursera $CONDA_DIR/lib/$d; done

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN rm requirements.txt

COPY ./jupyter-extension/nbextensions/submit-button $CONDA_DIR/jupyter-extension/jupyter/nbextensions/submit-button
RUN jupyter nbextension install $CONDA_DIR/jupyter-extension/jupyter/nbextensions/submit-button && \
    jupyter nbextension enable submit-button/main

COPY ./jupyter-extension/.jupyter/ /home/$NB_USER/.jupyter/

RUN fix-permissions /home/$NB_USER/.jupyter
ENV PYTHONWARNINGS ignore

# Install jq
ENV JQ_VERSION='1.5'

RUN apt-get update && sudo apt-get install -y gnupg && \
    wget --no-check-certificate https://web.archive.org/web/20230315053723/https://raw.githubusercontent.com/stedolan/jq/master/sig/jq-release.key -O /tmp/jq-release.key && \
    wget --no-check-certificate https://raw.githubusercontent.com/jqlang/jq/master/sig/v${JQ_VERSION}/jq-linux64.asc -O /tmp/jq-linux64.asc && \
    wget --no-check-certificate https://github.com/jqlang/jq/releases/download/jq-${JQ_VERSION}/jq-linux64 -O /tmp/jq-linux64 && \
    gpg --import /tmp/jq-release.key && \
    gpg --verify /tmp/jq-linux64.asc /tmp/jq-linux64 && \
    cp /tmp/jq-linux64 /usr/bin/jq && \
    chmod +x /usr/bin/jq && \
    rm -f /tmp/jq-release.key && \
    rm -f /tmp/jq-linux64.asc && \
    rm -f /tmp/jq-linux64

RUN python -m textblob.download_corpora

# Need to run as root for grader to write into /shared/feedback.json
# we have user namespaces enabled
#USER $NB_USER

# Enable all nbgrader extensions
# RUN jupyter labextension enable --level=sys_prefix nbgrader && \
#     jupyter serverextension enable --sys-prefix --py nbgrader

# Persist git configuration options
RUN ln -s /home/$NB_USER/work/.dotfiles-coursera/.gitconfig /home/$NB_USER/.gitconfig
RUN ln -s /home/$NB_USER/work/.dotfiles-coursera/.git-credentials /home/$NB_USER/.git-credentials

VOLUME /shared

RUN fix-permissions /home/jovyan/.jupyter

ENV DOCKER_STACKS_JUPYTER_CMD=lab

EXPOSE 8888

USER root

RUN fix-permissions /home/jovyan/.jupyter

EXPOSE 8888
WORKDIR /home/$NB_USER/work
COPY nbgrader-files/release/nbgrader_config.py ./nbgrader_config.py

ENTRYPOINT ["/coursera/setup.sh"]

USER $NB_USER
