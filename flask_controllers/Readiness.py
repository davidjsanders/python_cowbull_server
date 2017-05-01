from flask.views import MethodView


class Readiness(MethodView):
    def get(self):
        return "ToDo"
