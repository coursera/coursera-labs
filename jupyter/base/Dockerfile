ARG BASE_IMAGE_NAME
ARG BASE_IMAGE_TAG=python-3.10.6
FROM ${BASE_IMAGE_NAME}:${BASE_IMAGE_TAG}

# Prepend FROM base-image
USER root

COPY .jupyter/ /home/$NB_USER/.jupyter/
RUN fix-permissions /home/$NB_USER/.jupyter
ENV PYTHONWARNINGS ignore

# Persist git configuration options
RUN ln -s /home/$NB_USER/work/.dotfiles-coursera/.gitconfig /home/$NB_USER/.gitconfig
RUN ln -s /home/$NB_USER/work/.dotfiles-coursera/.git-credentials /home/$NB_USER/.git-credentials
COPY gitconfig.sh /usr/local/bin/start-notebook.d/

# Set entry point
EXPOSE 8888
WORKDIR /home/$NB_USER/work
ENTRYPOINT ["tini", "--"]
CMD ["start-notebook.sh"]

# Force launch into notebook
ENV DOCKER_STACKS_JUPYTER_CMD=notebook

USER $NB_USER
