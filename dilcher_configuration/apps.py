from django.apps import AppConfig


class DilcherConfigurationConfig(AppConfig):
    name = 'dilcher_configuration'

    def ready(self):
        # The import below is not unused! It registers signals on all subclasses in different apps
        import dilcher_configuration.signals        # NOQA
