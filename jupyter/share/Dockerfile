# Prepend FROM base-image
USER root

# Add submit button, copy for each version of python in the kernel
COPY coursera /tmp/coursera
RUN for d in $(ls $CONDA_DIR/lib | grep "^python*") ; do cp -r /tmp/coursera $CONDA_DIR/lib/$d; done

COPY nbextensions/submit-button $CONDA_DIR/share/jupyter/nbextensions/submit-button
RUN jupyter nbextension install $CONDA_DIR/share/jupyter/nbextensions/submit-button && \
    jupyter nbextension enable submit-button/main

COPY .jupyter/ /home/$NB_USER/.jupyter/
RUN fix-permissions /home/$NB_USER/.jupyter
ENV PYTHONWARNINGS ignore

# Set entry point
EXPOSE 8888
WORKDIR /home/$NB_USER/work
ENTRYPOINT ["tini", "--"]
CMD ["start-notebook.sh"]

USER $NB_USER
