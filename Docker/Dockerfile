FROM python:3.10-slim

WORKDIR /app

RUN pip install --upgrade pip && pip install transformers torch

COPY setup/testscript.py ./

CMD ["python", "testscript.py"]
