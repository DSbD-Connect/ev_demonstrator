FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN apt update
RUN apt install curl procps -y
EXPOSE 5001

CMD ["python", "hw-manager.py"]