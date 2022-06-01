#!/bin/sh

# Invoke docker container to run `coursera-lab.py` script
if [ "$1" = "build" ] || [ "$1" = "run" ] || [ "$1" = "test" ]; then
ACTION=$1
BUILD_DIR="$(cd "$(dirname "$2")"; pwd)"
BUILD_PATH="$BUILD_DIR/$(basename "$2")"

ADD_SUBMIT_BUTTON=$3

docker run \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $BUILD_DIR:/$BUILD_DIR \
  -e HOME=$HOME \
  -v $HOME/.coursera:$HOME/.coursera \
  -it \
  run-lab python3 coursera-lab.py $ACTION $BUILD_PATH $ADD_SUBMIT_BUTTON
else 
  docker run -it run-lab python3 coursera-lab.py '--help'
fi

