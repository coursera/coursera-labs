## Coursera Labs

### Quick Start

Install [Docker](https://docs.docker.com) before you get started. `run-lab/coursera-lab.py` is a 
Docker client wrapper for Coursera Labs. This script simulates Coursera build and run 
procedures configured by the `manifest.json` file.

Below is an example of `manifest.json` file.                   
```json
{
  "name": "coursera/tensorflow-notebook",
  "version": "1.0",
  "httpPort": 8888,
  "mounts": [
    {
      "path": "/home/jovyan/work"
    }
  ],
  "environmentVars": [
    {
      "name": "NAME",
      "value": "VALUE"
    }
  ]
}
```
* **name**: the image name
* **version**: optional, the image tag
* **httpPort**: the exposed port of the container
* **mounts**: optonal, bind mount list of volumes to the container
* **environmentVars**: optional, list of environment variables of the container

**Build run-lab image** and then you can start using `run-lab/run.sh` script to simulate 
Coursera Labs build or run procedures.
```
docker build -t run-lab -f run-lab/Dockerfile .
```

**Example #1**: Build tensorflow-notebook image under build directory 
`jupyter/tensorflow-notebook`. `Dockerfile` and `manifest.json` are required to start the build.
```
./run-lab/run.sh build jupyter/tensorflow-notebook
```
**Example #2**: Build tensorflow-notebook image with Coursera submit button.
```
./run-lab/run.sh build jupyter/tensorflow-notebook --add-submit-button
```
**Example #3**: Run an instance of the built tensorflow-notebook image.
```
./run-lab/run.sh run jupyter/tensorflow-notebook
```
If you see `Tell me which volumes to mount for the following container volumes`, enter the 
volumes to be mounted. You'll see `Starting instance of coursera/tensorflow-notebook listening on
 localhost:14941`. Then go to `localhost:14941` in your browser to play with the tensorflow 
 notebook.
