import logging

# Import python_cowbull_server initialization package
# ---------------------------------------------------
# Import the app from the python_cowbull_server package, which will also
# load the __init__.py for the package. In effect, this allows sets up
# key variables, configuration, and other general settings and also
# defines the Flask app there, making it importable everywhere without
# circular references.
from python_cowbull_server import app, error_handler

# Import the Flask controllers for this app
# -----------------------------------------
# This enables request handlers to be defined outside of app.py making them
# more object-oriented and easier to manage and maintain.
from flask_controllers import GameServerController, HealthCheck, Readiness, GameModes

# Import the Flask routes
# -----------------------
# Currently, there is only a V1, but you get the idea if there were a V2.
from Routes.V1 import V1

# Add cross origin scripting support
# ----------------------------------
@app.after_request
def allow_cors(resp):
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return resp

# Version 1 routes
# ----------------
# Setup the version 1 routes.
v1 = V1(error_handler=error_handler, app=app)
v1.game(controller=GameServerController)
error_handler.log(message="Added route v1.game", logger=logging.info)

v1.modes(controller=GameModes)
error_handler.log(message="Added route v1.modes", logger=logging.info)

v1.health(controller=HealthCheck)
error_handler.log(message="Added route v1.health", logger=logging.info)

v1.readiness(controller=Readiness)
error_handler.log(message="Added route v1.readiness", logger=logging.info)

# DEV USE ONLY! Built-in Web Server
#----------------------------------
# If app.py has been run using Python, initiate a Flask object; otherwise,
# any caller (e.g. uWSGI or gunicorn) should initiate workers and routes.
# The code below is useful because it allows changes to be checked using
# Flask's built-in webserver (before building a Docker image) simply by
# running "python app.py". If using this method, remember:
#
# 1. instruct the app on how to find redis by setting environment variables
#    (see python_cowbull_server/__init__.py)
# 2. do not use for production workloads! The Flask webserver is suitable
#    for dev / test workloads only.
#
if __name__ == "__main__":
    error_handler.log(
        module="app.py",
        method="__main__",
        message="Running application via Flask built-in server.",
        logger=logging.info
    )
    application = app
    application.debug = True
    application.run()
#    app.run\
#        (
#            host=app.config["FLASK_HOST"],
#            port=int(app.config["FLASK_PORT"]),
#            debug=app.config["FLASK_DEBUG"]
#        )
