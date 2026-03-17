FROM python:3.11-slim

WORKDIR /backend

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--reload", "--proxy-headers", "--host", "0.0.0.0", "--port", "5000"]