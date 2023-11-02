##### BASE IMAGE #####
FROM elixircloud/foca:20221110-py3.10

##### METADATA #####
LABEL version="3.0"
LABEL software="proWES"
LABEL software.description="Flask microservice implementing the Global Alliance for Genomics and Health (GA4GH) Workflow Execution Service (WES) API specification as a proxy for middleware injection (e.g., workflow distribution logic)."
LABEL software.website="https://github.com/elixir-europe/proWES"
LABEL software.documentation="https://github.com/elixir-europe/proWES"
LABEL software.license="https://spdx.org/licenses/Apache-2.0"
LABEL maintainer="cloud-service@elixir-europe.org"
LABEL maintainer.organisation="ELIXIR Cloud & AAI"

# Python UserID workaround for OpenShift/K8S
ENV LOGNAME=ipython
ENV USER=ipython

WORKDIR /app
COPY ./ .
RUN pip install -e .

## Add permissions for storing updated API specification
## (required by FOCA)
RUN chmod -R a+rwx /app/pro_wes/api
