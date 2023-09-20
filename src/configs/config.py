import logging

import yaml
from schema import Schema, SchemaError

logger = logging.getLogger("app")


class Config:
    def __init__(self, config_path: str, schema: Schema) -> None:
        self.config_path = config_path
        self.schema = schema

        self.config = self.load_config()

    def get(self):
        return self.config

    def load_config(self) -> dict:
        data = self.load_config_data()
        self.validate_config(data)
        return data

    def load_config_data(self):
        try:
            with open(self.config_path, "r") as configfile:
                config = yaml.load(configfile, Loader=yaml.FullLoader)
                return config
        except FileNotFoundError:
            logging.error(f"{self.config_path} not found")
            raise FileNotFoundError

    def validate_config(self, data):
        try:
            self.schema.validate(data)
        except SchemaError as e:
            logger.error(f"Config file not valid: {e}")
            raise ValueError

    def write_config(self) -> None:
        with open(self.config_path, "w") as configfile:
            yaml.dump(self.config, configfile)

    def write_config_decorator(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.write_config()

        return wrapper

    def read_config_decorator(func):
        def wrapper(self, *args, **kwargs):
            self.bot_config = self.load_config()
            return func(self, *args, **kwargs)

        return wrapper

    @read_config_decorator
    def __getitem__(self, key: str) -> str:
        return self.config[key]

    @write_config_decorator
    def __setitem__(self, key: str, value: str) -> None:
        self.config[key] = value

    def __contains__(self, item):
        return item in self.config
