FROM python:3.8

WORKDIR /app

COPY Pipfile /app
COPY Pipfile.lock /app
COPY main.py /app
COPY app /app/app
COPY .env /app

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN apt-get install -y python3.8-dev
RUN apt-get install -y gcc

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pipenv
RUN python3 -m pip install pycryptodome
RUN python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps dssdm
RUN pipenv install --system --deploy --dev
RUN python3 -m pip uninstall bson -y
RUN python3 -m pip uninstall pymongo -y
RUN python3 -m pip install pymongo
RUN python3 -m pip install requests
RUN python3 -m pip install pyOpenSSL

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]