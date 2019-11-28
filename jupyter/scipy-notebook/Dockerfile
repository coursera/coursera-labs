FROM jupyter/scipy-notebook:135a595d2a93

RUN fix-permissions /home/jovyan/.jupyter

RUN conda install --quiet --yes -c potassco clingo

USER $NB_USER
