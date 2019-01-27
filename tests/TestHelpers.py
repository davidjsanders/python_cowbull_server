from flask_helpers.check_kwargs import check_kwargs
from unittest import TestCase

class TestHelpers(TestCase):

    def test_kw_check_kwargs(self):
        self.assertTrue(check_kwargs(
            parameter_list=["a","b","c"],
            caller="test_check_kwargs",
            **{"a":1, "b":2, "c":3}
        ))

    def test_kw_empty_kwargs(self):
        self.assertTrue(check_kwargs(
            parameter_list=["a","b","c"],
            caller="test_check_kwargs",
            **{}
        ))

    def test_kw_no_params(self):
        with self.assertRaises(ValueError):
            check_kwargs(
                parameter_list=[],
                caller="test_kw_bad_args",
                **{"x": 2}
            )

    def test_kw_bad_args(self):
        with self.assertRaises(TypeError):
            check_kwargs(
                parameter_list=["a","b"],
                caller="test_kw_bad_args",
                **{"x": 2}
            )