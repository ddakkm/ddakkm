FROM tiangolo/uvicorn-gunicorn:python3.8

ENV PORT 8080
COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt



COPY ./app ./app
COPY ./app/env/*.env ./
