import logging
from TestGameServerController import TestGameServerController
from TestGameController import TestGameController
from TestGameObject import TestGameObject
from TestHelpers import TestHelpers
from TestPersister import TestPersister
from TestPersisterMongo import TestPersisterMongo
from TestPersisterRedis import TestPersisterRedis
from TestFlaskControllers import TestFlaskControllers
from TestHealthCheck import TestHealthCheck
from TestGameMode import TestGameMode
from TestGameModes import TestGameModes

from python_cowbull_server import app
from Routes.V1 import V1
from flask_helpers.ErrorHandler import ErrorHandler
from flask_controllers import GameServerController
from flask_controllers import HealthCheck
from flask_controllers import Readiness
from flask_controllers import GameModes


logging.disable(logging.CRITICAL)
error_handler = ErrorHandler()
v1 = V1(error_handler=error_handler, app=app)
v1.game(controller=GameServerController)
v1.modes(controller=GameModes)
v1.health(controller=HealthCheck)
v1.readiness(controller=Readiness)
