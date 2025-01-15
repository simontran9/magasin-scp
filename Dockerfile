FROM ubuntu:latest

WORKDIR /app

RUN apt update

RUN apt install -y python3 python3-pip python3-dev libpq-dev

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY application.py /app

COPY magasinscp/ /app

CMD ["python3", "application.py"] 