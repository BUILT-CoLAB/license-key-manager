FROM python:3.9

WORKDIR /license-key-manager

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "server.py"]