FROM python:3.9

RUN pip install flask mysql-connector-python

RUN mkdir -p /app/pages

COPY ./app /app
COPY ./pages /app/pages
COPY ./init.sql /app/init.sql

RUN echo "HITS{LFI_4ft3r_SQLi_1s_D0uble_Fun}" > /app/flag.txt && \
    chmod 744 /app/flag.txt

WORKDIR /app
CMD ["python", "app.py"]