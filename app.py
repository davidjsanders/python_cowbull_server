# Import the controllers and helpers for this app
from flask_controllers import GameController, HealthCheck, Readiness, GameModes
from flask_helpers.ErrorHandler import ErrorHandler

# Import the app from the python_cowbull_server Python package. This allows
# us to define the app there and have it importable throughout the app.
# Importing the app also enables the configuration to be executed in the
# __init__.py code.
from python_cowbull_server import app
print("INITIALIZATION: App imported")

# Setup an error handler and configure logging based on the config
# variables LOGGING_LEVEL and LOGGING_FORMAT (see __init__.py for
# default values.)
errorHandler = ErrorHandler(module="app.py", method="Initialization")
errorHandler.basicConfig(
    level=app.config.get("LOGGING_LEVEL", 20),
    format=app.config.get("LOGGING_FORMAT",
                          "/home/devdsanders/Documents/dev/python_cowbull_server/vendor/kubeconfig/cowbull.cfg")
)

# Add a game view. The game view is actually contained within a class
# based on a MethodView. See flask_controllers/GameController.py
errorHandler.log(message="Adding game URL: {}/game".format(app.config["GAME_VERSION"]))
game_view = GameController.as_view('Game')
app.add_url_rule(
    '/{0}/game'.format(app.config["GAME_VERSION"]),
    view_func=game_view,
    methods=["GET", "POST"]
)

# Add a game modes view. The game modes view is actually contained within a class
# based on a MethodView. See flask_controllers/GameModes.py
errorHandler.log(message="Adding game URL: {}/modes".format(app.config["GAME_VERSION"]))
modes_view = GameModes.as_view('Modes')
app.add_url_rule(
    '/{0}/modes'.format(app.config["GAME_VERSION"]),
    view_func=modes_view,
    methods=["GET"]
)

# Add a health check view so that infrastructure, such as Kubernetes or AWS ECS, can
# check the health of the application. This check simply returns a 200 status and
# can be probed at regular occassions to check the responsiveness (of the pod,
# container, etc.)
errorHandler.log(message="Adding health check URL: {}/health".format(app.config["GAME_VERSION"]))
health_view = HealthCheck.as_view('Health')
app.add_url_rule(
    '/{0}/health'.format(app.config["GAME_VERSION"]),
    view_func=health_view,
    methods=["GET"]
)

# Add a readiness view. The code below currently does nothing other than return an
# HTML 200 status. In a more complex app, it could return a 503 error (service
# unavailable), so that a scheduling engine like Kubernetes or a load balancer
# could avoid sending traffic to the node until it responds ready (200).
errorHandler.log(message="Adding readiness check URL: {}/ready".format(app.config["GAME_VERSION"]))
readiness_view = Readiness.as_view('ready')
app.add_url_rule(
    '/{0}/ready'.format(app.config["GAME_VERSION"]),
    view_func=readiness_view,
    methods=["GET"]
)

# If app.py has been run using Python, initiate a Flask object; otherwise, any
# caller (e.g. uWSGI or gunicorn) should initiate workers and routes. The code
# below is useful because it allows changes to be checked using Flask's built-in
# webserver (before building a Docker image) simply by running "python app.py".
# If using this method, remember:
#
# 1. instruct the app on how to find redis by setting environment variables (see
#    python_cowbull_server/__init__.py)
# 2. do not use for production workloads! The Flask webserver is suitable for
#    dev / test workloads only.
#
if __name__ == "__main__":
    app.run\
        (
            host=app.config["FLASK_HOST"],
            port=app.config["FLASK_PORT"],
            debug=app.config["FLASK_DEBUG"]
        )
