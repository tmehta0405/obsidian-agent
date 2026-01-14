FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agent.py .
COPY texts/ ./texts/
COPY .env .
RUN mkdir -p test_vault
CMD ["python", "agent.py"]