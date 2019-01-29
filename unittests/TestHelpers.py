import json
import logging
import sys
from unittest import TestCase
from flask_helpers.build_response import build_response
from flask_helpers.check_kwargs import check_kwargs
from flask_helpers.ErrorHandler import ErrorHandler
from flask_helpers.VersionHelpers import VersionHelpers
from werkzeug.datastructures import Headers
from flask import Response

class TestHelpers(TestCase):
    def setUp(self):
        pass

    def test_he_br_response(self):
        r = build_response(
            200, 
            "String response", 
            response_mimetype="application/json"
        )
        mimetype = r.mimetype.encode("utf-8")
        return_data = r.get_data()
        self.assertIsInstance(r, Response)
        self.assertIsInstance(r.headers, Headers)
        self.assertIs(r.status_code, 200)
        self.assertEqual(mimetype, "application/json".encode("utf-8"))
        self.assertEqual(return_data.decode("utf-8"), '{"result": "String response"}')

    def test_he_br_jsondata(self):
        r = build_response(
            200,
            {"foo": "bar", "value": 100, "torf": False}
        )
        self.assertIsInstance(r, Response)

    def test_he_br_bad_jsondata(self):
        with self.assertRaises(TypeError):
            build_response(
                200,
                {"foo": build_response(200, "test"), "value": 100, "torf": False}
            )

    def test_he_br_bad_status(self):
        with self.assertRaises(TypeError):
            build_response({"status": 200})

    def test_he_br_low_status(self):
        with self.assertRaises(ValueError):
            build_response(50)

    def test_he_kw_check_kwargs(self):
        self.assertTrue(check_kwargs(
            parameter_list=["a","b","c"],
            caller="test_check_kwargs",
            **{"a":1, "b":2, "c":3}
        ))

    def test_he_kw_empty_kwargs(self):
        self.assertTrue(check_kwargs(
            parameter_list=["a","b","c"],
            caller="test_check_kwargs",
            **{}
        ))

    def test_he_kw_no_params(self):
        with self.assertRaises(ValueError):
            check_kwargs(
                parameter_list=[],
                caller="test_kw_bad_args",
                **{"x": 2}
            )

    def test_he_kw_bad_args(self):
        with self.assertRaises(TypeError):
            check_kwargs(
                parameter_list=["a","b"],
                caller="test_kw_bad_args",
                **{"x": 2}
            )

    def test_he_eh_init(self):
        eh = ErrorHandler(
            module="test_he",
            method="test_he_eh_init",
            level=logging.ERROR
        )
        self.assertIsInstance(eh, ErrorHandler)

    def test_he_bad_module(self):
        with self.assertRaises(TypeError):
            ErrorHandler(
                module=-2,
                method="test_he_eh_init",
                level=10
            )

    def test_he_bad_method(self):
        with self.assertRaises(TypeError):
            ErrorHandler(
                module="test_he",
                method=10,
                level=10
            )

    def test_he_check_error(self):
        eh = ErrorHandler(
            module="TEST",
            method="TEST-METHOD",
            level=logging.INFO
        )
        message = "Message for testing purposes only"
        exception = "IGNORE Testing"
        r = eh.error(status=404, message=message, exception=exception)
        r_data=json.loads(r.get_data())
        self.assertEqual(r_data["status"], 404)
        self.assertEqual(r_data["message"], message)
        self.assertEqual(r_data["exception"], exception)

    def test_he_check_warn(self):
        eh = ErrorHandler(
            module="TEST",
            method="TEST-METHOD",
            level=logging.ERROR
        )
        message = "Message for testing purposes only"
        eh.log(
            status=404, 
            message=message, 
            logger=logging.warning
        )

    def test_he_vh_init(self):
        vh = VersionHelpers()
#        isinstance(vh.STRINGTYPE, basestring)
        self.assertTrue(
            vh.STRINGTYPE, basestring if sys.version_info[0] < 3 else str
        )