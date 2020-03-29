import json
import fastjsonschema as schema
import re
import os


class ConfigParserError(Exception):
    pass


class ConfigFileError(ConfigParserError):
    pass


class ConfigValidationError(ConfigParserError):
    pass


JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "token": {"type": "string"},
        "path_to_cities": {"type": "string"},
        "logs_path": {"type": "string"}
    }
}


def parse_config(path_to_file: str) -> dict:
    try:
        with open(path_to_file, "r", encoding="utf8") as config_file:
            config = json.load(config_file)
            if validate_config(config):
                return config
            else:
                raise ConfigValidationError(f"Failed to validate config: {config}")
    except IOError:
        raise ConfigFileError(f"An error occurred while reading config file: {path_to_file}")


def validate_token(token: str) -> bool:
    match = re.fullmatch("[0-9]{9}:[a-zA-Z0-9_]{35}", token)
    return match is not None


def validate_path_to_existent_file(path: str) -> bool:
    return os.path.isfile(path)


def validate_path_file(path: str) -> bool:
    dirname = os.path.dirname(path)
    return os.path.isdir(dirname)


VALIDATORS = {
    "token": validate_token,
    "path_to_cities": validate_path_to_existent_file,
    "logs_path": validate_path_file
}


def validate_config(config: dict) -> bool:
    try:
        schema.validate(JSON_SCHEMA, config)
    except schema.JsonSchemaException:
        return False
    else:
        for key, value in config.items():
            if not VALIDATORS[key](value):
                return False
        return True


if __name__ == '__main__':
    print("Script for parsing config")
