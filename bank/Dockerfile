FROM python:alpine
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
CMD ["python", "main.py"]
