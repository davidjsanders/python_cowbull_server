# Initialization code. Placed in a separate Python package from the main
# app, this code allows the app created to be imported into any other
# package, module, or method.

import logging          # Import standard logging - for levels only

from python_cowbull_server.Configurator import Configurator
from flask import Flask # Import Flask

# Instantiate the Flask application as app
app = Flask(__name__)
c = Configurator(app)
logging.basicConfig(
    level=app.config["LOGGING_LEVEL"],
    format=app.config["LOGGING_FORMAT"]
)
