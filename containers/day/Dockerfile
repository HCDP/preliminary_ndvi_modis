FROM ghcr.io/hcdp/task-preliminary-ndvi-modis-base:latest
LABEL org.opencontainers.image.source="https://github.com/hcdp/preliminary_ndvi_modis"
LABEL org.opencontainers.image.description="Daily NDVI Aggregation and Mapping."

WORKDIR /workspace/dependencies
RUN wget -nv https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/workflow_data/preliminary/ndvi_modis/dependencies/daily_dependencies.tar.gz
RUN tar -xf daily_dependencies.tar.gz
RUN rm daily_dependencies.tar.gz

ADD /code/day /workspace/code
# Get the container's upload config as specified in the code repo.
ADD /containers/day/configs/upload.json /sync/config.json
# Add the task wrapper script.
ADD /containers/day/task.sh /workspace/task.sh

WORKDIR /workspace
# This container is intended to run the task wrapper at launch, unless otherwise specified at run-time.
CMD [ "/bin/bash", "task.sh" ]
