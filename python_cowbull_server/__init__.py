import logging
import os
from flask import Flask


app = Flask(__name__)
try:
    app.config.from_pyfile(os.environ.get("COWBULL_CONFIG", "config/cowbull.cfg"))
except FileNotFoundError:
    app.config["LOGGING_FORMAT"] = os.getenv(
        "LOGGING_FORMAT",
        "%(asctime)s %(levelname)s: %(message)s"
    )
    app.config["LOGGING_LEVEL"] = os.getenv("LOGGING_LEVEL", logging.INFO)
    try:
        if isinstance(app.config["LOGGING_LEVEL"], str):
            app.config["LOGGING_LEVEL"] = int(app.config["LOGGING_LEVEL"])
    except ValueError:
        app.config["LOGGING_LEVEL"] = logging.INFO

    app.config["FLASK_HOST"] = os.getenv("FLASK_HOST", "0.0.0.0")
    app.config["FLASK_PORT"] = os.getenv("FLASK_PORT", 5000)
    app.config["FLASK_DEBUG"] = os.getenv("FLASK_DEBUG", True)
    if isinstance(app.config["FLASK_DEBUG"], str):
        if app.config["FLASK_DEBUG"].lower() == "false":
            app.config["FLASK_DEBUG"] = False
        else:
            app.config["FLASK_DEBUG"] = bool(app.config["FLASK_DEBUG"])

    app.config["GAME_VERSION"] = os.getenv("GAME_VERSION", "v0_1")

    app.config["REDIS_HOST"] = os.getenv("REDIS_HOST", "redis")
    app.config["REDIS_PORT"] = os.getenv("REDIS_PORT", 6379)
    app.config["REDIS_DB"] = os.getenv("REDIS_DB", 0)
    app.config["REDIS_USEAUTH"] = False

