FROM python:3.13-slim

ENV TZ=Asia/Tehran

WORKDIR /photoebot

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8

CMD ["python", "b.py"]

