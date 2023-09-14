FROM python:3.10

WORKDIR /app

COPY ./req.txt .
RUN pip install -r req.txt

COPY . .

CMD ["python", "main.py"]
