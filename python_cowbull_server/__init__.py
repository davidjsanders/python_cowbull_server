# Initialization code. Placed in a separate Python package from the main
# app, this code allows the app created to be imported into any other
# package, module, or method.

import logging          # Import standard logging - for levels only

from python_cowbull_server.Configurator import Configurator
from flask import Flask
from flask_helpers.ErrorHandler import ErrorHandler

# Instantiate the Flask application as app
app = Flask(__name__)

# Instantiate a configurator object
c = Configurator()

# Load the configuration
c.execute_load(app)

# Grab the error handler from the configuration object
error_handler = c.error_handler

# print the variables defined to stdout.
c.print_variables()

if app.config["COWBULL_DRY_RUN"]:
    error_handler.log(
        method="__init__",
        module="python_cowbull_server",
        message="Dry run set. No executiong. Terminating.",
        logger=logging.warning
    )
    print("Dry run env. var. is set. Exiting...")
    exit(0)

error_handler.log(
    method="__init__",
    module="python_cowbull_server",
    message="Initialization complete.",
    logger=logging.info
)