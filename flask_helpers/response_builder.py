from flask import Response


def response_builder(
    html_status=None,
    response_data=None,
    response_mimetype=None
):
    if html_status is None:
        html_status = 200
    if response_mimetype is None:
        response_mimetype = "application/json"

    return Response(
        response=response_data,
        mimetype=response_mimetype,
        status=html_status
    )
