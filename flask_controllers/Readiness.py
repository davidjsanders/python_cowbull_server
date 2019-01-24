from flask.views import MethodView
from flask_helpers.build_response import build_response


class Readiness(MethodView):
    def get(self):
        return build_response(
            html_status=200,
            response_data={"status": "ready"},
            response_mimetype="application/json"
        )
