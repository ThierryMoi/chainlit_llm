FROM python:3.9

WORKDIR /app

COPY . /app

RUN ls
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python3","main.py"]