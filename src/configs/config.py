import logging

import yaml
from schema import Schema, SchemaError

logger = logging.getLogger("app")


class Config:
    def __init__(self, config_path: str, schema: Schema) -> None:
        self._config_path = config_path
        self._schema = schema

        self._config_data = self.load_config()

    def get(self):
        return self._config_data

    def load_config(self) -> dict:
        data = self._load_config_data()
        self.validate_config(data)
        return data

    def _load_config_data(self):
        try:
            with open(self._config_path, "r") as configfile:
                config = yaml.load(configfile, Loader=yaml.FullLoader)
                return config
        except FileNotFoundError:
            logging.error(f"{self._config_path} not found")
            raise FileNotFoundError

    def validate_config(self, data):
        try:
            self._schema.validate(data)
        except SchemaError as e:
            logger.error(f"Config file not valid: {e}")
            raise ValueError

    def write_config(self) -> None:
        with open(self._config_path, "w") as configfile:
            yaml.dump(self._config_data, configfile)

    def _write_config_decorator(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.write_config()

        return wrapper

    def _read_config_decorator(func):
        def wrapper(self, *args, **kwargs):
            self.bot_config = self.load_config()
            return func(self, *args, **kwargs)

        return wrapper

    @_read_config_decorator
    def __getitem__(self, key: str) -> str:
        return self._config_data[key]

    @_write_config_decorator
    def __setitem__(self, key: str, value: str) -> None:
        self._config_data[key] = value

    def __contains__(self, item):
        return item in self._config_data
