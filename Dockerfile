FROM python:3.8.2

WORKDIR /.

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
