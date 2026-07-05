FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY monitorBroker.py .

CMD ["python", "-u", "monitorBroker.py"]