"""
Post AI generated text to Telegram chat or channel

Usage:
  ai_to_tg.py [-c <config_file>] [-p <custom_prompt>] [-d] [-a]
  ai_to_tg.py (-h | --help)

Options:
  -c <config_file>     Path to config file [default: .config.yaml]
  -p <custom_prompt>   Custom prompt to pass to the OpenAI
  -d                   Enable verbose output (DEBUG level)
  -a                   Enable auto posting
  -h --help            Show this help message.
"""

import sys
import logging
import random
import requests
import yaml
from docopt import docopt
from openai import OpenAI

def setup_logger(verbose=False):
    """Sets up basic logger with optional verbose output."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")
    return logging.getLogger("ai_to_tg")


def parse_yaml_config(config_path, logger):
    """
    Parses a YAML configuration file and returns the data as a dictionary.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        dict: Parsed YAML content as a dictionary.
    """
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        logger.error(f"Error: File not found - {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error: {e}")
        sys.exit(1)
    return {}


def ask_llm(config, custom_prompt, logger):
    """
    Send request to Open AI model. Combined from config["preamble"] and topic.

    Args:
        config (dict): Config dictionary.
        custom_prompt (str): Custom request, provided to the application with -p option.

    Returns:
        str: Response from Open AI.
    """
    client = OpenAI(api_key=config["openai_key"])

    topic = custom_prompt if custom_prompt is not None else random.choice(config["topics"])
    logger.info(f"topic: {topic}")

    prompt = config["preamble"] + topic
    response = client.responses.create(
        model=config["ai_model"],
        input=prompt
        )

    return str(response.output_text)


def post_to_tg(config, text, autopost, logger):
    """
    Post text to Telegram channel or chat via Tg API /sendMessage

    Args:
        config (dict): Config dictionary.
        text (str): Text to be sent.
        autopost (bool): Indicates if post will be sent automatically or not.
    """
    tg_url = f"https://api.telegram.org/bot{config['tg_key']}/sendMessage"
    logger.info(text)

    if not autopost:
        choice = input("Continue with this post? (y/n): ").strip().lower()
        if choice != "y":
            sys.exit(0)

    logger.info("Posting...")

    params = {
        "chat_id": config["tg_chat"],
        "text": text.replace("**", "*"), # hack to ensure bold text displayed correctly
        "parse_mode": "Markdown"  
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(tg_url, json=params, headers=headers, timeout=10)
        logger.info(response.status_code)
        logger.debug(response.json())
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to post to Telegram: {e}")
        sys.exit(1)


def main():
    """Main function"""
    args = docopt(__doc__)
    config_path = args["-c"]
    custom_prompt = args["-p"]
    verbose = args["-d"]
    autopost = args["-a"]

    logger = setup_logger(verbose)
    logger.debug("Custom string provided: %s", custom_prompt)
    logger.debug("Arguments received: %s", args)

    config = parse_yaml_config(config_path, logger)

    required_keys = ["openai_key", "tg_key", "tg_chat", "ai_model", "preamble", "topics"]
    for key in required_keys:
        if key not in config:
            logger.error("Missing required config key: %s", key)
            sys.exit(1)

    logger.debug("\nFinal parsed config:")
    logger.debug(config)

    resulting_text = ask_llm(config, custom_prompt, logger)
    post_to_tg(config, resulting_text, autopost, logger)


if __name__ == "__main__":
    main()
