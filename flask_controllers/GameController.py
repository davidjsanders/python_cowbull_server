import json
from flask import Flask
from flask.views import MethodView
from flask_helpers.response_builder import response_builder


class GameController(MethodView):
    def get(self):
        return response_builder(
            html_status=200,
            response_data=json.dumps("Hello World0"),
            response_mimetype="application/json"
        )

    def post(self):
        return None