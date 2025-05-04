# oa2tg - OpenAI to Telegram Bot

A Python utility that generates AI-based text using OpenAI and posts it to a Telegram chat or channel.
This is a small experimental tool, feel free to use and modify.

## Features

- Generates content using OpenAI models.
- Supports custom prompts or random topic selection.
- Sends generated content to a Telegram bot.
- Optional interactive confirmation before posting.
- Configurable via a YAML file.
- Supports verbose/debug logging.

## Requirements

For local development environment:

- Python 3.7+
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- `requests`, `pyyaml`, `docopt`

Install dependencies with `pip`:

```bash
pip install -r requirements.txt
```

## Usage

```bash
Post AI generated text to Telegram chat or channel

Usage:
  ai_to_tg.py [-c <config_file>] [-p <custom_string>] [-d] [-a]
  ai_to_tg.py (-h | --help)

Options:
  -c <config_file>     Path to config file [default: .config.yaml]
  -p <custom_prompt>   Custom prompt to pass to the OpenAI
  -d                   Enable verbose output (DEBUG level)
  -a                   Enable auto posting
  -h --help            Show this help message.
```

## Configuration File

Create a `.config.yaml` with the following structure:

```yaml
openai_key: "your_openai_api_key"
ai_model: "gpt-4.1-mini"  # or gpt-3.5-turbo, etc.
preamble: "Please write an insightful post about: "
topics:
  - "the future of AI in education"
  - "why remote work is here to stay"
  - "ethical implications of machine learning"
tg_key: "your_telegram_bot_token"
tg_chat: "@your_channel_or_chat_id"
```

## Prerequisites

- [OpenAI key](https://platform.openai.com/api-keys)
- [Telegram Bot's token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)


## Quickstart

The recommended way to run this app is using Docker. To build the Docker image, run:

```bash
docker build -t oa2tg:latest .
```

## Examples

- Randomly select topic and post with preview:

    ```bash
    docker run -it -v `pwd`/.config.yaml:/app/.config.yaml oa2tg:latest
    ```

- Set topic manually and post with preview:

    ```bash
    docker run -it -v `pwd`/.config.yaml:/app/.config.yaml oa2tg:latest -p "My custom prompt here"
    ```

- Set topic manually and post automatically:

    ```bash
    docker run -v `pwd`/.config.yaml:/app/.config.yaml oa2tg:latest -p "My custom prompt here" -a
    ```

- Set topic automatically and post automatically. Display debug logs:

    ```bash
    docker run -v `pwd`/.config.yaml:/app/.config.yaml oa2tg:latest -a -d
    ```

## Known issues

Sometimes the response of OpenAI might be too long so telegram API will reject it.
In this case the prompt needs to be fine-tuned.
