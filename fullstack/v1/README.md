_This is a test image for FullStack-MOOC. It is based on the the standard VSCODE image._

## Coursera Labs Fullstack Installation

### Quick Start 

_Adapted from coursera-labs README_

1. **Install [Docker](https://docs.docker.com)** if not installed already

2. **Build run-lab image**
    Open a terminal and run the following from the parent directory (i.e. `coursera-labs`).

    ```
    docker build -t run-lab -f run-lab/Dockerfile .
    ```
    
    The `run-lab` image is a Dockerized version of `run-lab/coursera-lab.py` script. `run-lab/coursera-lab.py` script simulates Coursera Labs Docker build and run procedures.

3. **Build `fullstack/v1` image locally**

    ```bash
    ./run-lab/run.sh build fullstack/v1
    ```

4. **Test `fullstack/v1` image locally**

    ```bash
    ./run-lab/run.sh run fullstack/v1
    ```

    You will be prompted to indicate which volumes to mount for the container. This is where you can mount a directory from your computer by passing the **absolute** path to that folder. 
    
*     For example, on a Mac, you might store all coding projects at `/Users/{your-user-name}/Projects`. Let's say you have a version of the React Intro project. So, at the prompt, you should enter `/Users/{your-user-name}/Projects/coursera-mooc/react-intro`.

    You will also be asked to indicate the volume to mount for `/data/db`.

    Once you select the volumes to mount, press `Enter` to continue and you will see a message showing which port the docker image is running on. 

    **Example message:**
    
    ```bash
    Starting instance of fullstack-v1 listening on localhost:13515
    ```

    Open a web browser, go to the port and you should find the project there.

### Considerations for Docker Container

* Project files from the folder you mounted in the step above will be available in the container at `/home/coder/project/`. Once you visit localhost:**{PORT}** and VSCode loads, you will be able to open the project folder at `/home/coder/project/`.

**Remember to run `npm install` to add all project dependencies.**

Within the container, be sure to check the `webpack.config.js`. Within the container, the VSCode instance will be running on port `8080` (as specified in `fullstack/v1/manifes.json`). 

In order to ensure this port doesn't clash with the project running inside the docker container, you may need to update the `webpack.config.js` to specify the port the project app should use. 

**Example `webpack.config.js`**:

```js
module.exports = {
  //...
  devServer: { 
    port: 9000, // add a port other than 8080
  },
};
```	

### Using Cypress in Docker Container

Run the following commands in a separate terminal.

1.  To install cypress:

    ```bash
    ./node_modules/.bin/cypress install
    ```

2.  To run cypress in headless mode:

    ```bash
    ./node_modules/.bin/cypress run
    ```

The results of the cypress tests will be displayed in the terminal. Also, you will notice that videos for each of the test suites are output to the `cypress/videos` directory.
