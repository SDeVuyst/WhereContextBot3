FROM python:3.8.2

WORKDIR /.

COPY . .

RUN pip install --no-cache-dir -r requirements.txt