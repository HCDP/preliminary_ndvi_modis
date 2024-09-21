# Start with the Air Temperature Preliminary Aggregation Base.
FROM ghcr.io/hcdp/task-preliminary-ndvi-modis-base:latest
LABEL org.opencontainers.image.source="https://github.com/hcdp/task-ndvi-modis-daily"
LABEL org.opencontainers.image.description="Daily NDVI Aggregation and Mapping."

RUN mkdir -p /workspace/code
RUN mkdir -p /workspace/config

ADD /code/day /workspace/code
# Get the container's upload config as specified in the code repo.
ADD /containers/day/configs/upload.json /workspace/config/config.json
# Add the task wrapper script.
ADD /containers/day/task.sh /workspace/task.sh

WORKDIR /workspace
# This container is intended to run the task wrapper at launch, unless otherwise specified at run-time.
CMD [ "/bin/bash", "task.sh" ]
