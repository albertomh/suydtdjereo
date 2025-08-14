from django.apps import AppConfig
from django.core import checks


class SuydtdjereoConfig(AppConfig):
    name = "suydtdjereo"

    def ready(self) -> None:
        from suydtdjereo.checks import check_dev_mode, check_model_names

        checks.register(check_dev_mode)
        checks.register(check_model_names)
