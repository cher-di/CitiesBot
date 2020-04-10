import csv
import argparse

from scripts.bot.bot import Bot
from scripts.config.parse_config import parse_config, ConfigParserError


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

    try:
        config = parse_config(args["config_file_path"])
    except ConfigParserError as e:
        print(e)
        exit(1)
    else:
        token = config["token"]

        with open(config["cities_db_file_path"], "r", encoding="utf8") as file:
            reader = csv.reader(file)
            _cities = tuple(row[0] for row in reader)

        bot = Bot(token, _cities, config["logs_file_path"])
        bot.run()
