FROM python:3.12-alpine3.21

WORKDIR /app

RUN apk add --no-cache postgresql-client libpq gcc musl-dev postgresql-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
