import unittest
from unittest.mock import patch, mock_open, MagicMock
import logging
import oa2tg
import sys


class TestOA2TG(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("test")
        self.config = {
            "openai_key": "fake_key",
            "tg_key": "fake_tg_key",
            "tg_chat": "@fakechannel",
            "ai_model": "gpt-test",
            "preamble": "Write about: ",
            "topics": ["cats", "dogs"],
        }

    @patch("builtins.open", new_callable=mock_open, read_data="openai_key: test_key")
    @patch("yaml.safe_load", return_value={"openai_key": "test_key"})
    def test_parse_yaml_config_success(self, mock_yaml_load, mock_open_file):
        config = oa2tg.parse_yaml_config("fake_path.yaml", self.logger)
        self.assertIn("openai_key", config)
        mock_open_file.assert_called_once()

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_parse_yaml_config_file_not_found(self, mock_open_file):
        with self.assertRaises(SystemExit):
            oa2tg.parse_yaml_config("nonexistent.yaml", self.logger)

    @patch("yaml.safe_load", side_effect=Exception("Bad YAML"))
    @patch("builtins.open", new_callable=mock_open, read_data=":bad_yaml")
    def test_parse_yaml_config_yaml_error(self, mock_open_file, mock_yaml):
        with self.assertRaises(Exception) as context:
            oa2tg.parse_yaml_config("bad.yaml", self.logger)
        self.assertIn("Bad YAML", str(context.exception))

    @patch("oa2tg.OpenAI")
    def test_ask_llm_with_custom_prompt(self, mock_openai):
        mock_response = MagicMock()
        mock_response.output_text = "Generated text"
        mock_openai.return_value.responses.create.return_value = mock_response

        result = oa2tg.ask_llm(self.config, "test topic", self.logger)
        self.assertIn("Generated text", result)
        mock_openai.assert_called_once()

    @patch("builtins.input", return_value="y")
    @patch("requests.post")
    def test_post_to_tg_manual_post_accepted(self, mock_post, mock_input):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        oa2tg.post_to_tg(self.config, "Hello, Telegram!", False, self.logger)
        mock_post.assert_called_once()

    @patch("builtins.input", return_value="n")
    def test_post_to_tg_manual_post_rejected(self, mock_input):
        with self.assertRaises(SystemExit):
            oa2tg.post_to_tg(self.config, "Should not post", False, self.logger)

    @patch("requests.post", side_effect=Exception("Telegram error"))
    def test_post_to_tg_exception(self, mock_post):
        with self.assertRaises(Exception) as context:
            oa2tg.post_to_tg(self.config, "Test text", True, self.logger)
        self.assertIn("Telegram error", str(context.exception))

    def test_setup_logger_debug_level(self):
        logger = oa2tg.setup_logger(verbose=True)
        self.assertEqual(logger.getEffectiveLevel(), logging.DEBUG)

    def test_setup_logger_info_level(self):
        # Create a clean logger to avoid interference
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logger = oa2tg.setup_logger(verbose=False)
        self.assertEqual(logger.getEffectiveLevel(), logging.INFO)


if __name__ == "__main__":
    unittest.main()
