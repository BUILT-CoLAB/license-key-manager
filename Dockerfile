FROM python:3.9

WORKDIR /license-manager

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install gunicorn

COPY ./bin /license-manager/bin
COPY .env /license-manager/bin


CMD ["gunicorn", "-w 1", "-b 0.0.0.0", "--preload", "bin:create_app()"]