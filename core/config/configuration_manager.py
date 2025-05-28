from decouple import config


class ConfigurationManager:
    @staticmethod
    def x_api_key():
        return config("X_API_KEY")

    @staticmethod
    def db_engine():
        return config("DB_ENGINE", default='django.db.backends.postgresql')

    @staticmethod
    def db_name():
        return config("POSTGRES_DB", default='postgres')

    @staticmethod
    def db_host():
        return config("POSTGRES_HOST", default='localhost')

    @staticmethod
    def db_port():
        return config("POSTGRES_PORT", default='5432')

    @staticmethod
    def db_username():
        return config("POSTGRES_USER", default='postgres')

    @staticmethod
    def db_password():
        return config("POSTGRES_PASSWORD", default='postgres')

    @staticmethod
    def replica_host():
        return config("POSTGRES_REPLICA_HOST", default='localhost')
