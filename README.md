## Coursera Labs

This repository provides resources for creating custom images on Coursera Labs. This resource may be particularly helpful for those looking to add small modifications to the existing default images on Coursera Labs, which are included in this repository.

### Quick Start

1. **Install [Docker](https://docs.docker.com)** if not installed already

2. **Build run-lab image**
    ```
    docker build -t run-lab -f run-lab/Dockerfile .
    ```
    The `run-lab` image is a Dockerized version of `run-lab/coursera-lab.py` script. `run-lab/coursera-lab.py` script simulates Coursera Labs Docker build and run procedures.

3. **Create a folder with your custom image files and `manifest.json`**

    The folders `jupyter/datascience-notebook`, `jupyter/scipy-notebook` and `jupyter/tensorflow-notebook` include the files that build our base images. Please feel free to use these folders to test out this build flow.

    We also *strongly* recommend using the provided images as the basis for your custom images.

    Additionally, Coursera Labs script uses `manifest.json` to read configurations specific to your image. Details about `manifest.json` can be found [here](#manifestjson).

4. **Build and Test your custom image locally**

    Build jupyter notebook image
    ```
    ./run-lab/run.sh build <path to image folder> --add-submit-button
    ```
    You can find the generated `Dockerfile` with the commands to add submit button under `<path to image folder>/generated` folder.

    Build image of an application other than Jupyter Notebook
    ```
    ./run-lab/run.sh build <path to image folder>
    ```
    Run an instance of the built custom image
    ```
    ./run-lab/run.sh run <image name>
    ```
    If you see a message that asks: `Tell me which volumes to mount for the following container volumes`, enter the local machine path from which files are to be mounted at that specific mount path.

    You'll see a message that says `Starting instance of <image-name> listening on localhost:<port>`. Then go to `localhost:<port>` in your browser to play with the custom image.

### Manifest.json

Coursera Labs script uses `manifest.json` to read configurations specific to your image. Below is an example of `manifest.json` file.                   
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
* **mounts**: mount list of volumes to the container. Files mounted at these mount paths persist across lab sessions in Coursera Labs. In other words, you need at least one mount path to persist files across lab sessions.
* **environmentVars**: optional, list of environment variables of the container

### Examples
**Example #1**: Build tensorflow-notebook image under build directory `jupyter/tensorflow-notebook`. `Dockerfile` and `manifest.json` are required to start the build.
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
