FROM python:3.8-slim-buster

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

#EXPOSE 8001
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "app:app"]