FROM python:3.12-slim

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY /requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY /app /app

WORKDIR /app
ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
