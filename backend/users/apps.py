from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "users"
    def ready(self):
        # import signals to ensure signal handlers are connected
        from . import signals  # noqa: F401
