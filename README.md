## Coursera Labs

### Quick Start

1. **Install [Docker](https://docs.docker.com)** if not installed already

2. **Build run-lab image**
    ```
    docker build -t run-lab -f run-lab/Dockerfile .
    ```
    run-lab image is a dockerized version of `run-lab/coursera-lab.py` script. `run-lab/coursera-lab.py` script simulates Coursera Labs docker build and run procedures.
    
3. **Create a folder with your custom image files and `manifest.json`**

    We strongly recommend to use our example images `jupyter/datascience-notebook`, `jupyter/scipy-notebook` or `jupyter/tensorflow-notebook` as a base of your image. 
    Coursera labs script uses `manifest.json` to read configurations specific to your image. Details about `manifest.json` can be found [here](#manifestjson)
    
4. **Build and Test your custom image locally**

    Build jupyter notebook image
    ```
    ./run-lab/run.sh build <path to image folder> --add-submit-button
    ```
    Build image of application other than jupyter notebook
    ```
    ./run-lab/run.sh build <path to image folder>
    ```
    Run an instance of the built custom image
    ```
    ./run-lab/run.sh run <image name>
    ```
    If you see a message like `Tell me which volumes to mount for the following container volumes`, enter the local machine path from which files are to be mounted at that specific mount path. 
    You'll see a message like `Starting instance of <image-name> listening on localhost:<port>`. Then go to `localhost:<port>` in your browser to play with the custom image.

### Manifest.json
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
* **mounts**: optonal, mount list of volumes to the container. Files mounted at these mount paths persist across lab sessions in Coursera labs.
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
