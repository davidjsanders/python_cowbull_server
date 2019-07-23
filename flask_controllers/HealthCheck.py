from flask.views import MethodView
from flask_helpers.build_response import build_response
from python_cowbull_server import app, error_handler


class HealthCheck(MethodView):
    def get(self):
        self.persistence_engine = app.config.get("PERSISTER", None)
        if not self.persistence_engine:
            raise ValueError(
                "No persistence engine is defined and for some unknown "
                "reason, the default of redis did not make it through "
                "configuration!"
            )

        _response = {
            "health": "checking",
            "comment": "Setting defaults - if seen, something has gone wrong in HealthCheck.py"
        }
        _status = 500

        try:
            persister = self.persistence_engine.persister
            persister.save("healthcheck", "OK")
            _response = {
                "health": "ok",
                "comment": "Able to persist"
            }
            _status = 200
        except Exception as e:
            _response = {
                "health": "notok",
                "comment": "Unable to persist {}".format(str(e))
            }

        return build_response(response_data=_response, html_status=_status)
