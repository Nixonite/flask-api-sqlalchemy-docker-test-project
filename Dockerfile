FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y runit python-pip python-dev \
    build-essential redis-server
RUN pip install --upgrade pip

COPY . .
RUN pip install -r requirements.txt

COPY gunicorn-config.py /etc/gunicorn/config.py

EXPOSE 80

COPY run.sh /etc/service/app/run
RUN chmod +x /etc/service/app/run

COPY runit.sh /runit.sh

ENTRYPOINT ["/runit.sh"]
