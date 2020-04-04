import json
import argparse


CONFIG_TEMPLATE = {
        "token": "<token>",
        "cities_db_file_path": "<path_to_the_file with cities>",
        "logs_file_path": "<path_to_the_logs_file>"
    }


def generate_config_template(path_to_file: str) -> None:
    with open(path_to_file, "w", encoding="utf8") as config_file:
        json.dump(CONFIG_TEMPLATE, config_file, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create template for config file")
    parser.add_argument("file_path", help="Path to template config file")
    file_path = parser.parse_args().file_path

    try:
        generate_config_template(file_path)
    except IOError:
        print(f"An error occurred while writing config template to {file_path}")
