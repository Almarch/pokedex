FROM python:latest

RUN pip install --upgrade pip
RUN pip install --no-cache-dir build

WORKDIR /app
COPY ./myAgent /app/myAgent

RUN pip install --no-cache-dir /app/myAgent

EXPOSE 80
CMD ["python", "-m", "myAgent", "0.0.0.0", "80"]
