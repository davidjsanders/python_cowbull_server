from flask.views import MethodView
from flask_helpers.build_response import build_response


class HealthCheck(MethodView):
    def get(self):
        _response = {
            "health": "ok"
        }
        _status = 200

        return build_response(response_data=_response, html_status=_status)
