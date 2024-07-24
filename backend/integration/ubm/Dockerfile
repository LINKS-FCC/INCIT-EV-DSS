FROM python:3.9

RUN apt-get update
RUN apt-get install -y software-properties-common && apt-get update
RUN apt-get install -y gdal-bin libgdal-dev
RUN apt-get install -y gcc

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --upgrade --no-cache-dir setuptools==57.5.0
RUN python3 -m pip install -r requirements.txt

ENV PYTHONPATH=${PYTHONPATH}:${PWD} 

COPY . .