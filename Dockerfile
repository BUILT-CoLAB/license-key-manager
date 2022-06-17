FROM python:3.9

WORKDIR /license-manager

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8150

CMD [ "python3", "server.py"]