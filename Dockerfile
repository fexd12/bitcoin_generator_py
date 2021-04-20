# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-alpine

WORKDIR /app

COPY . .

RUN python -m venv venv

RUN venv/bin/python -m pip install --upgrade pip

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN venv/bin/pip install -r requirements.txt

CMD ["venv/bin/python","teste_ecc.py"]
