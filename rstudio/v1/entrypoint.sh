#!/bin/bash

# Add .hidden file to /home/rstudio to hide .rstudio folder for lab publishing
# .rstudio folder contains user session information that we don't want to publish to child labs
# More details about .rstudio in https://support.rstudio.com/hc/en-us/articles/218417097-Filling-up-the-home-directory-with-RStudio-Server
if ! grep -Fxqs ".rstudio" /home/rstudio/.hidden
then
  echo ".rstudio" >> /home/rstudio/.hidden
  chown rstudio:rstudio /home/rstudio/.hidden
fi

# Load workspace environment variables to R
if [ -n "$WORKSPACE_ENV_VARS" ]; then
  for envVar in ${WORKSPACE_ENV_VARS//,/ }
  do
      echo "$envVar=${!envVar}" >> "$R_HOME/etc/Renviron"
  done
fi

# Hand off to the CMD
exec "$@"
