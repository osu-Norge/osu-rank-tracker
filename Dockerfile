FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY . .

CMD ["python3", "src/run.py"]
