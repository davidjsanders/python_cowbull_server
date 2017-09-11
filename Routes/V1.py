from flask_helpers.ErrorHandler import ErrorHandler


#############################################################################
# Version 1 routes                                                          #
#############################################################################

class V1(object):
    def __init__(self, error_handler=None, app=None):
        if not isinstance(error_handler, ErrorHandler):
            raise TypeError("Expected an ErrorHandler to be passed!")
        if app is None:
            raise ValueError("App must be passed to the route object!")

        self.app = app

        self.error_handler = error_handler
        self.error_handler.module = "V1"
        self.error_handler.method = "__init__"
        self.error_handler.log(message="Initialized V1 Routes")

    def game(self, controller=None):
        # Add a game view. The game view is actually contained within a class
        # based on a MethodView. See flask_controllers/GameServerControllerroller.py
        # ---------------------------------------------------------------------------
        self.error_handler.method = "game"
        self.error_handler.log(message="Adding game URL: /v1/game")
        game_view = controller.as_view('Game')
        self.app.add_url_rule('/v1/game', view_func=game_view, methods=["GET", "POST"])

    def modes(self, controller=None):
        # Add a game modes view. The game modes view is actually contained within a class
        # based on a MethodView. See flask_controllers/GameModes.py
        # ---------------------------------------------------------------------------
        self.error_handler.method = "modes"
        self.error_handler.log(message="Adding game URL: /v1/modes")
        modes_view = controller.as_view('Modes')
        self.app.add_url_rule(
            '/v1/modes',
            view_func=modes_view,
            methods=["GET"]
        )

    def health(self, controller=None):
        # Add a health check view so that infrastructure, such as Kubernetes or AWS ECS, can
        # check the health of the application. This check simply returns a 200 status and
        # can be probed at regular occassions to check the responsiveness (of the pod,
        # container, etc.)
        # ---------------------------------------------------------------------------
        self.error_handler.method = "health"
        self.error_handler.log(message="Adding health check URL: /v1/health")
        health_view = controller.as_view('Health')
        self.app.add_url_rule(
            '/v1/health',
            view_func=health_view,
            methods=["GET"]
        )

    def readiness(self, controller=None):
        # Add a readiness view. The code below currently does nothing other than return an
        # HTML 200 status. In a more complex app, it could return a 503 error (service
        # unavailable), so that a scheduling engine like Kubernetes or a load balancer
        # could avoid sending traffic to the node until it responds ready (200).
        # ---------------------------------------------------------------------------
        self.error_handler.method = "readiness"
        self.error_handler.log(message="Adding readiness check URL: /v1/ready")
        readiness_view = controller.as_view('ready')
        self.app.add_url_rule(
            '/v1/ready',
            view_func=readiness_view,
            methods=["GET"]
        )
