## Coursera Labs

This repository provides resources for creating custom images on Coursera Labs. It includes files to build and run the (3) base images on Coursera Labs. This resource may be particularly helpful for those looking to add small modifications to the existing default images on Coursera Labs. You may also find it helpful to use these scripts to add a submit button for your own Jupyter Notebook images.

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

    Additionally, Coursera Labs script uses `manifest.json` to read configurations specific to your image. Details about `manifest.json` can be found [here](#image-configurations-using-manifestjson).

4. **Build your image locally**

    <b>Jupyter Notebook images</b>: Build Jupyter Notebook image by running the following command:
    ```
    ./run-lab/run.sh build <path to image folder> --add-submit-button
    ```
    This will create a new folder called `/generated` under your `<path to image folder>`.

    <b>Other web app images</b>: Build image of an application other than Jupyter Notebook by running the following command:
    ```
    ./run-lab/run.sh build <path to image folder>
    ```
5. **Test your image locally**
    Run an instance of the built custom image by running the following command:
    ```
    ./run-lab/run.sh run <path to image folder>
    ```
    For example, if you built the tensorflow-notebook image that we provided,
    ```
    ./run-lab/run.sh run jupyter/tensorflow-notebook
    ```
    If you see a message that asks: `Tell me which volumes to mount for the following container volumes`, enter the local machine path from which files are to be mounted at that specific mount path.

    You'll see a message that says `Starting instance of <image-name> listening on localhost:<port>`. Then go to `localhost:<port>` in your browser to play with the custom image.
    
6. **Upload your image to the platform**

    The build step should have created a folder called `/generated` under your `<path to image folder>`. In this folder, there will be a `Dockerfile` with all the relevant commands to build the image on the platform.

    If you do not need any folders or files outside of the `Dockerfile`, you can create a .zip of the `Dockerfile` and then upload it as a Custom Image to the Lab Manager using the "Upload Build Files" button.

    If you do need any folders or files to successfully build the image (e.g. `requirements.txt`), make sure to include these files in the `.zip` file such that the `Dockerfile` can reference it successfully during the build process. Make sure the `Dockerfile` is located in the root directory.
    
    You do not need to add `manifest.json` to the `.zip` file to upload successfully to the platform, unless your `Dockerfile` explicitly uses this.


### Image configurations using `manifest.json`

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
