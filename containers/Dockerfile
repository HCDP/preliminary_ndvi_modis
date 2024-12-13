FROM ghcr.io/hcdp/task-base:latest
LABEL org.opencontainers.image.source="https://github.com/hcdp/preliminary_ndvi_modis"
LABEL org.opencontainers.image.description="Base Image for preliminary NDVI Modis workflows."

RUN apt update

RUN pip install --upgrade pip

RUN pip install geemap
RUN pip install rasterio
RUN pip install numpy

RUN mkdir -p /gc-service-credentials
RUN mkdir -p /workspace/code
RUN mkdir -p /workspace/dependencies
RUN mkdir -p /workspace/envs
RUN mkdir -p /sync

RUN wget https://raw.githubusercontent.com/ikewai/data-uploader/main/upload.py -O /sync/upload.py

ADD /gc-service-credentials/gee-credentials.json /gc-service-credentials
ADD /tools /sync
ADD /envs/prod.env /workspace/envs