## Coursera Labs

This repository provides resources for creating custom images on Coursera Labs. It includes files to build and run images on Coursera Labs, including the source files to set up our (5) base images.

This resource may be particularly helpful for those looking to:

1) add small modifications to the existing default images on Coursera Labs
2) add a submit button or bypass the token authentication flow for your own Jupyter Notebook images

### Quick Start

1. **Install [Docker](https://docs.docker.com)** if not installed already

2. **Build run-lab image**

    ```
    docker build -t run-lab -f run-lab/Dockerfile .
    ```

    The `run-lab` image is a Dockerized version of `run-lab/coursera-lab.py` script. `run-lab/coursera-lab.py` script simulates Coursera Labs Docker build and run procedures.

3. **Create a folder with your custom image files and `manifest.json`**

    The folders `jupyter/datascience-notebook/v2`, `jupyter/scipy-notebook/v2` and `jupyter/tensorflow-notebook/v2` include the files that build our v2 base images. Please feel free to use these folders to test out this build flow.

    We also *strongly* recommend using the provided images as the basis for your custom images.

    Additionally, Coursera Labs script uses `manifest.json` to read configurations specific to your image. Details about `manifest.json` can be found [here](#image-configurations-using-manifestjson).

4. **Build your image locally**

    <b>Jupyter Notebook images</b>: Build Jupyter Notebook image by running the following command. The `--add-submit-button` option also takes care of the token authentication flow, so you should use this option for all Jupyter Notebook images you plan on using on Coursera Labs.

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
    ./run-lab/run.sh run jupyter/tensorflow-notebook/v2
    ```

    If you see a message that asks: `Tell me which volumes to mount for the following container volumes`, enter the local machine path from which files are to be mounted at that specific mount path.

    You'll see a message that says `Starting instance of <image-name> listening on localhost:<port>`. Then go to `localhost:<port>` in your browser to play with the custom image.

6. **Upload your image to the platform**

    The build step should have created a folder called `/generated` under your `<path to image folder>`. In this folder, there will be a `Dockerfile` with all the relevant commands to build the image on the platform.

    If you do not need any folders or files outside of the `Dockerfile`, you can create a .zip of the `Dockerfile` and then upload it as a Custom Image to the Lab Manager using the "Upload Build Files" button.

    If you do need any folders or files to successfully build the image (e.g. `requirements.txt`), make sure to include these files in the `.zip` file such that the `Dockerfile` can reference it successfully during the build process. Make sure the `Dockerfile` is located in the root directory.

    You do not need to add `manifest.json` to the `.zip` file to upload successfully to the platform, unless your `Dockerfile` explicitly uses this.

   **Port settings for custom images:** Note that by default, the custom Coursera lab builder will expose HTTP Port `8888`, the default port for Jupyter. If you are building a VS Code image, please set port to `8080`.

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

### Unit Tests

We're adding in unit testing frameworks to give us more confidence that our images do what we want them to do. For now, we only have unit tests in place for our nbgrader images, to verify that traceback redaction is working as expected. You can take advantage of these unit-tests with the command

```
./run-lab/run.sh test jupyter/nbgrader
```

You will be prompted to enter a filepath to which the rich feedback file will generated.

### Examples

**Example #1**: Build tensorflow-notebook v2 image under build directory `jupyter/tensorflow-notebook/v2`. `Dockerfile` and `manifest.json` are required to start the build.

```
./run-lab/run.sh build jupyter/tensorflow-notebook/v2
```

**Example #2**: Build tensorflow-notebook image with Coursera submit button. **This only works with Jupyter Notebook images.**

```
./run-lab/run.sh build jupyter/tensorflow-notebook/v2 --add-submit-button
```

**Example #3**: Run an instance of the built tensorflow-notebook image.

```
./run-lab/run.sh run jupyter/tensorflow-notebook/v2
```
