from flask_controllers import GameController, HealthCheck, Readiness
from flask_helpers.ErrorHandler import ErrorHandler
from python_cowbull_server import app

errorHandler = ErrorHandler(module="app.py", method="Initialization")
errorHandler.basicConfig(
    level=app.config["LOGGING_LEVEL"],
    format=app.config["LOGGING_FORMAT"]
)

# Add game view
errorHandler.log(message="Adding game URL: {}/game".format(app.config["GAME_VERSION"]))
game_view = GameController.as_view('Game')
app.add_url_rule(
    '/{0}/game'.format(app.config["GAME_VERSION"]),
    view_func=game_view,
    methods=["GET", "POST"]
)

# Add health view
errorHandler.log(message="Adding health check URL: {}/health".format(app.config["GAME_VERSION"]))
health_view = HealthCheck.as_view('Health')
app.add_url_rule(
    '/{0}/health'.format(app.config["GAME_VERSION"]),
    view_func=health_view,
    methods=["GET"]
)

# Add readiness view
errorHandler.log(message="Adding readiness check URL: {}/ready".format(app.config["GAME_VERSION"]))
readiness_view = Readiness.as_view('ready')
app.add_url_rule(
    '/{0}/ready'.format(app.config["GAME_VERSION"]),
    view_func=readiness_view,
    methods=["GET"]
)

#
# If app.py has been run using Python, initiate a Flask object;
# otherwise, any caller (e.g. uWSGI or gunicorn) should initiate
# workers and routes.
if __name__ == "__main__":
    app.run\
        (
            host=app.config["FLASK_HOST"],
            port=app.config["FLASK_PORT"],
            debug=app.config["FLASK_DEBUG"]
        )
