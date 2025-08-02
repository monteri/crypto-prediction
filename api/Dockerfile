FROM python:3.13-alpine

WORKDIR /api

# Install curl and netcat for network connectivity
RUN apk add --no-cache curl netcat-openbsd

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

ENV RUNTIME=run

CMD ["sh", "-c", "fastapi $RUNTIME main.py --port 9090 --host 0.0.0.0"]