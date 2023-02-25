from aiobotocore.session import get_session
from aws_lambda_powertools import Logger

class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Session(metaclass=Singleton):
    def __init__(self):
        self._session = None
        self._logger = Logger(child=True)

    @property
    def session(self):
        if self._session is None:
            self._session = get_session()
            self._logger.info("Session created")

        return self._session
