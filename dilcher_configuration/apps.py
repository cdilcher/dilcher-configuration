from django.apps import AppConfig


class DilcherConfigurationConfig(AppConfig):
    name = 'dilcher_configuration'

    def ready(self):
        import dilcher_configuration.signals
