from django.apps import AppConfig


class RedisAppConfig(AppConfig):
    name = 'redis_app'

    def ready(self):
        import redis_app.signals  # noqa: F401
