import json
import argparse


CONFIG_TEMPLATE = {
        "token": "<token>",
        "path_to_cities": "<path_to_the_file with cities>",
        "logs_path": "<path_to_the_logs_file>"
    }


def generate_config_template(path_to_file: str) -> None:
    with open(path_to_file, "w", encoding="utf8") as config_file:
        json.dump(CONFIG_TEMPLATE, config_file, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create template for config file")
    parser.add_argument("path_to_file", help="Path to template config file")
    path_to_file = parser.parse_args().path_to_file

    try:
        generate_config_template(path_to_file)
    except IOError:
        print(f"An error occurred while writing config template to {path_to_file}")
