import json
import fastjsonschema as schema


class ConfigParserError(Exception):
    pass


class ConfigValidationError(ConfigParserError):
    pass


class ConfigReadError(ConfigParserError):
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
        raise ConfigParserError(f"An error occurred while reading config file: {path_to_file}")


def validate_config(config: dict) -> bool:
    try:
        schema.validate(JSON_SCHEMA, config)
    except schema.JsonSchemaException:
        return False
    else:
        return True


if __name__ == '__main__':
    print("Script for parsing config")
