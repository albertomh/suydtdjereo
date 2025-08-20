import json
import logging

from django.test import Client, SimpleTestCase, override_settings
from parameterized import parameterized

from suydtdjereo.logging import FirstArgOnlyFilter, LoggingConfigFactory


class TestFirstArgOnlyFilter(SimpleTestCase):
    def setUp(self):
        self.filter = FirstArgOnlyFilter()
        self.record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_path",
            lineno=123,
            msg="Test message",
            args=("First argument", "Second argument"),
            exc_info=None,
        )

    def test_filter_logs_first_arg_as_msg(self):
        filtered = self.filter.filter(self.record)
        self.assertTrue(filtered)
        self.assertEqual(self.record.msg, "First argument")
        self.assertEqual(self.record.args, ())

    def test_filter_null_args_preserves_msg(self):
        self.record.args = None
        filtered = self.filter.filter(self.record)
        self.assertTrue(filtered)
        self.assertEqual(self.record.msg, "Test message")
        self.assertIsNone(self.record.args)


class LoggingConfigFactoryTest(SimpleTestCase):
    @parameterized.expand(
        [
            (True, [["console_dev"], ["console_http"], ["null"], ["console_dev"]]),
            (False, [["console_prod"], ["null"], ["console_prod"], ["console_prod"]]),
        ]
    )
    def test_build(self, debug_value, expected_handlers):
        factory = LoggingConfigFactory(debug=debug_value)
        config = factory.build()

        self.assertEqual(len(config["filters"]), 3)
        self.assertEqual(len(config["formatters"]), 3)
        self.assertEqual(len(config["handlers"]), 4)
        self.assertEqual(config["loggers"]["django"]["handlers"], expected_handlers[0])
        self.assertEqual(
            config["loggers"]["django.server"]["handlers"], expected_handlers[1]
        )
        self.assertEqual(
            config["loggers"]["django_structlog"]["handlers"], expected_handlers[2]
        )
        self.assertEqual(all({v["propagate"] for v in config["loggers"].values()}), False)
        self.assertEqual(config["root"]["handlers"], expected_handlers[3])


class LogsFormatTest(SimpleTestCase):
    """Test logs format based on DEBUG mode in Django runserver."""

    def setUp(self):
        self.client = Client()

    # NB. If this test is failing, check that DEBUG is not set as an environment variable
    # in the context / shell the test suite is running in.
    @override_settings(LOGGING=LoggingConfigFactory(debug=False).build())
    def test_logs_format_debug_false(self):
        req_logger = logging.getLogger("django.server")
        struct_logger = logging.getLogger("django_structlog")

        with self.assertNoLogs(req_logger, level="INFO"):
            self.client.get("/")
        with self.assertLogs(struct_logger, level="INFO") as log:
            self.client.get("/")
            logs_output = log.output[1]  # get the `request_finished` log
            json_part = logs_output.split("INFO:django_structlog.middlewares.request:")[1]
            json_part = json_part.replace("'", '"').replace("None", "null")
            log_dict: dict = json.loads(json_part)

            expected_keys = {
                "code",
                "event",
                "ip",
                "level",
                "logger",
                "request",
                "request_id",
                "timestamp",
                "user_id",
            }
            expected_values = {
                "event": "request_finished",
                "logger": "django_structlog.middlewares.request",
                "request": "GET /",
            }
            self.assertEqual(
                set(log_dict.keys()),
                expected_keys,
                "Log contains unexpected keys or missing keys",
            )
            for k in expected_values.keys():
                self.assertEqual(log_dict[k], expected_values[k], f"{k} should match")

    # Hard to test because Django loads logging configuration once, at startup (and DEBUG
    # is False when running tests). This means @override_settings would apply only after
    # logging has been configured using DEBUG=False. Plus, the change to DEBUG would
    # involve popping the structlog middleware from MIDDLEWARES.
    # def test_logs_format_debug_true(self):
    #     ...
