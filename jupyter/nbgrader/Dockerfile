# Jupyter Notebook images with Nbgrader
# Requirements:
#   Argument BASE_IMAGE_NAME must be a valid Jupyter Notebook docker image
#
# Options:
#   Argument BASE_IMAGE_TAG may select a version other than latest

FROM 268845366347.dkr.ecr.us-east-1.amazonaws.com/base/datascience-notebook-v4.0

# Paths needed by nbgrader
ENV NBGRADER_FILES_PATH=/coursera/nbgrader-files
ENV GRADER_FILES_PATH=/coursera/grader
ENV JN_WORK_DIR=/home/$NB_USER/work

# Install nbgrader
RUN pip install -U \
    "jupyterlab<3.6" \
    nbgrader \
    lxml

USER root
RUN mkdir -p $GRADER_FILES_PATH
RUN mkdir -p $NBGRADER_FILES_PATH

# Add nbgrader files
COPY nbgrader-files/nbgrader-setup.sh /usr/local/bin/start-notebook.d/nbgrader-setup.sh
COPY nbgrader-files/ $NBGRADER_FILES_PATH
RUN chmod 777 -R $NBGRADER_FILES_PATH/
COPY setup.sh /coursera/setup.sh
RUN chmod 777 -R /coursera

# Add grid files
COPY grader/ $GRADER_FILES_PATH
RUN chmod 755 -R $GRADER_FILES_PATH
 
# May be needed due to formgrader being in the coursera directory
COPY coursera /tmp/coursera
RUN for d in $(ls $CONDA_DIR/lib | grep "^python*") ; do cp -r /tmp/coursera $CONDA_DIR/lib/$d; done

RUN fix-permissions /home/$NB_USER/.jupyter
ENV PYTHONWARNINGS ignore

# Install jq
ENV JQ_VERSION='1.5'

RUN apt-get update && sudo apt-get install -y gnupg && \
    wget -O jq https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 && \ 
    chmod +x ./jq && \
    cp jq /usr/bin

# Need to run as root for grader to write into /shared/feedback.json
VOLUME /shared

RUN fix-permissions /home/jovyan/.jupyter

USER root

WORKDIR /home/$NB_USER/work
COPY nbgrader-files/release/nbgrader_config.py ./nbgrader_config.py

ENTRYPOINT ["/coursera/setup.sh"]
