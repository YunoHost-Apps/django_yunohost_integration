from django.apps import AppConfig


class YunohostIntegrationConfig(AppConfig):
    name = 'django_yunohost_integration'
    verbose_name = 'Yunohost Integration'

    def ready(self):
        from django_yunohost_integration import system_checks  # noqa - Register checks
