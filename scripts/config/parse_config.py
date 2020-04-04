import json
import os
import re
import fastjsonschema
import argparse
import pprint


class ConfigParserError(Exception):
    pass


class ConfigFileError(ConfigParserError):
    def __init__(self, file_path: str):
        self._file_path = file_path


class ConfigFileNotExists(ConfigFileError):
    def __str__(self):
        return f"Config file not exists: {self._file_path}"


class ConfigFileInvalidJsonFormat(ConfigFileError):
    def __str__(self):
        return f"Config file has invalid json format: {self._file_path}"


class ConfigFileInvalidJsonSchema(ConfigFileError):
    def __str__(self):
        return f"Config file has invalid json schema: {self._file_path}"


class ConfigFileReadError(ConfigFileError):
    def __str__(self):
        return f"An error occurred when reading config file: {self._file_path}"


class ConfigFilePathTypeError(ConfigFileError):
    def __str__(self):
        return f"Expected type 'str' for config file path, got '{type(self._file_path)}' instead"


class ConfigInvalidParameter(ConfigParserError):
    def __init__(self, pair: tuple):
        self._parameter, self._value = pair

    def __str__(self):
        return f"Invalid parameter '{self._parameter}': '{self._value}'"


class ConfigParser:
    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "token": {"type": "string"},
            "cities_db_file_path": {"type": "string"},
            "logs_file_path": {"type": "string"}
        },
        "required": ["token", "cities_db_file_path", "logs_file_path"],
        "maxProperties": 3,
    }

    def __init__(self):
        self._validators = {
            "token": self.__class__._validate_token,
            "cities_db_file_path": self.__class__._validate_cities_db,
            "logs_file_path": self.__class__._validate_logs_file_path,
        }

    @staticmethod
    def _validate_file_exists(file_path: str) -> bool:
        return os.path.isfile(file_path)

    @staticmethod
    def _validate_dir_exists(dir_path: str) -> bool:
        return os.path.isdir(dir_path)

    @classmethod
    def _validate_token(cls, token: str) -> bool:
        return re.fullmatch(r"[0-9]+:[a-zA-Z0-9\-_]+", token) is not None

    @classmethod
    def _validate_cities_db(cls, file_path: str) -> bool:
        return cls._validate_file_exists(file_path)

    @classmethod
    def _validate_logs_file_path(cls, file_path: str) -> bool:
        return cls._validate_dir_exists(os.path.dirname(file_path))

    def parse(self, config_file_path: str) -> dict:
        if not isinstance(config_file_path, str):
            raise ConfigFilePathTypeError(config_file_path)

        if not self._validate_file_exists(config_file_path):
            raise ConfigFileNotExists(config_file_path)

        try:
            with open(config_file_path, "r", encoding="utf8") as config_file:
                config = json.load(config_file)
        except IOError:
            raise ConfigFileReadError(config_file_path)
        except json.JSONDecodeError:
            raise ConfigFileInvalidJsonFormat(config_file_path)

        try:
            fastjsonschema.validate(self.__class__.CONFIG_SCHEMA, config)
        except fastjsonschema.JsonSchemaException:
            raise ConfigFileInvalidJsonSchema(config_file_path)

        for parameter, validator in self._validators.items():
            value = config[parameter]
            if not validator(value):
                raise ConfigInvalidParameter((parameter, value))

        return config


def parse_config(config_file_path: str) -> dict:
    return ConfigParser().parse(config_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Tool for check of config file is OK")
    parser.add_argument("config_file_path",
                        help="Path to config file")
    config_file_path = parser.parse_args().config_file_path

    try:
        config = parse_config(config_file_path)
    except ConfigParserError as e:
        print("FAILED")
        print(e)
    else:
        print("OK")
        pprint.pprint(config)
