import csv
import argparse

from scripts.bot.bot import Bot
import scripts.config.parse_config as parse_config


def parse_arguments() -> dict:
    parser = argparse.ArgumentParser(description="Script to start bot")
    parser.add_argument("-c", "--config",
                        dest="path_to_config",
                        required=True,
                        help="Path to config file")
    args = parser.parse_args()

    path_to_config = args.path_to_config

    return {
        "path_to_config": path_to_config
    }


if __name__ == '__main__':
    args = parse_arguments()
    path_to_config = args["path_to_config"]

    try:
        config = parse_config.parse_config(path_to_config)
    except parse_config.ConfigValidationError:
        print("Config validation failed")
    except parse_config.ConfigFileError:
        print(f"Failed to read config file : {path_to_config}")
    else:
        token = config["token"]

        with open(config["path_to_cities"], "rt", encoding="utf8") as file:
            cities_info = csv.DictReader(file)
            _cities = tuple(row["city"] for row in cities_info)

        bot = Bot(token, _cities, config["logs_path"])
        bot.run()
