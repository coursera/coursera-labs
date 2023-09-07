FROM --platform=linux/amd64 python:3.8.1-slim

RUN apt-get update 
RUN apt-get install -y curl 
RUN curl -sSL https://get.docker.com/ | sh

ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

COPY run-lab/coursera-lab.py coursera-lab.py

COPY jupyter/share share

ENTRYPOINT ["/tini", "--"]
