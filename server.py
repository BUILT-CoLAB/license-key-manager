from waitress import serve
import os
import bin
from dotenv import load_dotenv

# Load Server Status
load_dotenv()
serverHost = os.environ.get("SERVER_HOST")
serverPort = os.environ.get("SERVER_PORT")
# ################################################

print("Serving request through :: http://" + serverHost + ":" + serverPort)
serve(bin.create_app(), host = serverHost, port = serverPort)