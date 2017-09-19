import io
import logging
from unittest import TestCase
from flask_helpers.ErrorHandler import ErrorHandler
from flask import Response
from python_cowbull_server import app


class TestErrorHandler(TestCase):
    def setUp(self):
        self.error_handler = ErrorHandler(
            module="TestErrorHandler",
            method="setUp"
        )
        self.app = app.test_client()
        if app.config["PYTHON_VERSION_MAJOR"] < 3:
            self.logging_type = io.BytesIO
        else:
            self.logging_type = io.StringIO

    def test_eh_instantiation(self):
        eh = ErrorHandler(module="test_module", method="test_method")
        self.assertIsInstance(eh, ErrorHandler)
        self.assertEqual(eh.module, "test_module")
        self.assertEqual(eh.method, "test_method")

    def test_eh_get_logger(self):
        logger = self.error_handler.logger
        self.assertIsInstance(logger, logging.RootLogger)

    def test_eh_error(self):
        self.error_handler.method = "test_eh_error"
        result = self.error_handler.error(
            status=400,
            exception="This is an exception for test purposes only",
            message="This is a message for test purposes only"
        )
        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_code, 400)

    def test_eh_logging(self):
        self.error_handler.method="test_eh_logging"
        test_message = "This is a test message for logging"
        eval_message = "{}: {}: {}\n".format(
            self.error_handler.module,
            self.error_handler.method,
            test_message
        )
        log_capture = self.logging_type()
        sh = logging.StreamHandler(stream=log_capture)

        logger = self.error_handler.logger
        logger.propagate = False

        current_log_level = logger.getEffectiveLevel()
        logger.setLevel(logging.INFO)
        logger.addHandler(hdlr=sh)

        self.error_handler.log(logger=logging.info, message=test_message)

        logger.removeHandler(hdlr=sh)
        logger.setLevel(current_log_level)

        logged_output = log_capture.getvalue()
        self.assertEqual(logged_output, eval_message)
