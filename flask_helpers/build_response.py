import json
from flask import Response


def build_response(
    html_status=None,
    response_data=None,
    response_mimetype=None
):
    _html_status = html_status or 200
    if not isinstance(_html_status, int):
        raise TypeError("HTML status must be an integere")

    if _html_status < 100:
        raise ValueError("HTML status cannot be less than 100!")

    _response_mimetype = response_mimetype or "application/json"
    _response_data = response_data or {}
    if isinstance(_response_data, str):
        _response_data = {"result": _response_data}

    return Response(
        response=json.dumps(_response_data),
        mimetype=_response_mimetype,
        status=_html_status
    )
