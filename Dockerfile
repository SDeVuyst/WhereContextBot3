FROM python:3.8.2

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . CODE
WORKDIR /code

RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg
