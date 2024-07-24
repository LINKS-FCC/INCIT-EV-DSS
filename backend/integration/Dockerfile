FROM python:3.9

RUN apt-get update
RUN apt-get install -y software-properties-common && apt-get update
# RUN apt-get install -y python3.9-dev
RUN apt-get install -y gdal-bin libgdal-dev
RUN apt-get install -y gcc
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN mkdir /app 

COPY /datasets /app/datasets
COPY /config /app/config
COPY /outputs /app/outputs
COPY poetry.lock /app
COPY pyproject.toml /app
COPY /app /app/app
COPY main.py /app
COPY ci-and-p-gui /app/ci-and-p-gui
COPY ci /app/ci
COPY ubm /app/ubm
COPY power /app/power
COPY requirements.txt /app
WORKDIR /app

ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
ENV PYTHONPATH=${PYTHONPATH}:/app:/app/power:/app/power/power
ENV PYTHONPATH=${PYTHONPATH}:/app:/app/ci:/app/ci/ci
ENV PYTHONPATH=${PYTHONPATH}:/app:/app/ubm:/app/ubm/ubm
ENV PYTHONPATH=${PYTHONPATH}:/app:/app/ci-and-p-gui:/app/ci-and-p-gui/gui

RUN python3 -m pip install --upgrade --no-cache-dir setuptools==57.5.0
RUN python3 -m pip install fastapi
RUN python3 -m pip install uvicorn 
RUN python3 -m pip install python-multipart
RUN python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps dssdm
RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install typing-extensions --upgrade 

EXPOSE 80

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]