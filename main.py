import csv
import argparse

from scripts.bot.bot import Bot
from scripts.config.parse_config import parse_config


def parse_arguments() -> dict:
    parser = argparse.ArgumentParser(description="Script to start bot")
    parser.add_argument("-c", "--config",
                        dest="config_file_path",
                        required=True,
                        help="Path to config file")
    args = parser.parse_args()

    return {
        "config_file_path": args.config_file_path,
    }


if __name__ == '__main__':
    args = parse_arguments()
    config = parse_config(args["config_file_path"])
    token = config["token"]

    with open(config["cities_db_file_path"], "rt", encoding="utf8") as file:
        cities_info = csv.DictReader(file)
        _cities = tuple(row["city"] for row in cities_info)

    bot = Bot(token, _cities, config["logs_file_path"])
    bot.run()
