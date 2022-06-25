##### BASE IMAGE #####
FROM elixircloud/foca:20220625-py3.10

##### METADATA #####
LABEL base.image="elixircloud/foca:20220625-py3.10"
LABEL version="2.0"
LABEL software="proWES"
LABEL software.version="0.15.0"
LABEL software.description="Flask microservice implementing the Global Alliance for Genomics and Health (GA4GH) Workflow Execution Service (WES) API specification."
LABEL software.website="https://github.com/elixir-europe/proWES"
LABEL software.documentation="https://github.com/elixir-europe/proWES"
LABEL software.license="https://github.com/elixir-europe/proWES/blob/master/LICENSE"
LABEL software.tags="General"
LABEL maintainer="alexander.kanitz@alumni.ethz.ch"
LABEL maintainer.organisation="Biozentrum, University of Basel"
LABEL maintainer.location="Klingelbergstrasse 50/70, CH-4056 Basel, Switzerland"
LABEL maintainer.lab="ELIXIR Cloud & AAI"
LABEL maintainer.license="https://spdx.org/licenses/Apache-2.0"

# Python UserID workaround for OpenShift/K8S
ENV LOGNAME=ipython
ENV USER=ipython

## Set working directory
WORKDIR /app

## Copy Python requirements
COPY ./requirements.txt /app/requirements.txt
COPY ./requirements_dev.txt /app/requirements_dev.txt

## Install Python dependencies
RUN cd /app \
  && pip install -r requirements.txt \
  && pip install -r requirements_dev.txt \
  && cd /

## Copy remaining app files
COPY ./ /app

## Install app
RUN cd /app \
  && python setup.py develop \
  && cd /
