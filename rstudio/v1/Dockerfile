FROM rocker/tidyverse:4.0.0

ENV DISABLE_AUTH true

RUN echo "session-timeout-minutes=0" >> /etc/rstudio/rsession.conf

# Install common r-packages
RUN R -e "install.packages(c('RColor', 'manipulate', 'proto', 'munsell', 'dichromat', 'RCurl', 'bitops', 'zoo', 'maps', 'sp', 'maptools', 'XML'), repos = 'http://cran.us.r-project.org', dependencies = TRUE)"

# Required for shiny to work
RUN R -e "install.packages('shiny', repos = 'http://cran.us.r-project.org', dependencies = TRUE)"

# Get LaTeX
RUN apt-get update && apt-get install --no-install-recommends -y texlive-full

COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

RUN git config --global core.fileMode false

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/init"]
