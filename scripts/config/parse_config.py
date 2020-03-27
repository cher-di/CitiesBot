import json


class ConfigParserError(Exception):
    pass


def parse_config(path_to_file: str) -> dict:
    try:
        with open(path_to_file, "r", encoding="utf8") as config_file:
            return json.load(config_file)
    except IOError:
        raise ConfigParserError(f"An error occurred while parsing {path_to_file}")


if __name__ == '__main__':
    print("Script for parsing config")
