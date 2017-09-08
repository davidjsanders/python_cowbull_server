# Import the app from the python_cowbull_server Python package. This allows
# us to define the app there and have it importable throughout the app.
# Importing the app also enables the configuration to be executed in the
# __init__.py code.
#
# ---------------------------------------------------------------------------
from python_cowbull_server import app

# Import the controllers and helpers for this app
# ---------------------------------------------------------------------------
from flask_controllers import GameServerController, HealthCheck, Readiness, GameModes
from Routes.V1 import V1
from flask_helpers.ErrorHandler import ErrorHandler


# Add cross origin scripting support
# ---------------------------------------------------------------------------
@app.after_request
def allow_cors(resp):
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return resp

# Setup an error handler and configure logging based on the config
# variables LOGGING_LEVEL and LOGGING_FORMAT (see __init__.py for
# default values.)
# ---------------------------------------------------------------------------
errorHandler = ErrorHandler(module="app.py", method="Initialization")
errorHandler.basicConfig(
    level=app.config.get("LOGGING_LEVEL", 20),
    format=app.config.get("LOGGING_FORMAT",
                          "%(asctime)s %(levelname)s: %(message)s")
)

#############################################################################
# Version 1 routes                                                          #
#############################################################################

v1 = V1(errorHandler=errorHandler, app=app)
v1.game(controller=GameServerController)
v1.modes(controller=GameModes)
v1.health(controller=HealthCheck)
v1.readiness(controller=Readiness)

#############################################################################
# Built-in Web Server                                                       #
#############################################################################
# If app.py has been run using Python, initiate a Flask object; otherwise,  #
# any caller (e.g. uWSGI or gunicorn) should initiate workers and routes.   #
# The code below is useful because it allows changes to be checked using    #
# Flask's built-in webserver (before building a Docker image) simply by     #
# running "python app.py". If using this method, remember:                  #
#                                                                           #
# 1. instruct the app on how to find redis by setting environment variables #
#    (see python_cowbull_server/__init__.py)                                #
# 2. do not use for production workloads! The Flask webserver is suitable   #
#    for dev / test workloads only.                                         #
#                                                                           #
#############################################################################
if __name__ == "__main__":
    app.run\
        (
            host=app.config["FLASK_HOST"],
            port=int(app.config["FLASK_PORT"]),
            debug=app.config["FLASK_DEBUG"]
        )
