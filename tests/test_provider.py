import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")
base_url = os.getenv("NVIDIA_BASE_URL")

import pytest
from unittest.mock import Mock, patch

from src.core.openai_provider import OpenAIProvider


class TestOpenAIProvider:
    @patch("src.core.openai_provider.OpenAI")
    def test_generate_without_system_prompt(self, mock_openai_cls):
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello from model"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        # Mock client
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        provider = OpenAIProvider(
            model_name="openai/gpt-oss-20b",
            api_key=api_key,
            base_url=base_url
        )

        result = provider.generate("Say hello")

        mock_client.chat.completions.create.assert_called_once_with(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": "Say hello"}],
        )

        assert result["content"] == "Hello from model"
        assert result["usage"] == {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        }
        assert result["provider"] == "openai"
        assert isinstance(result["latency_ms"], int)
        assert result["latency_ms"] >= 0

    @patch("src.core.openai_provider.OpenAI")
    def test_generate_with_system_prompt(self, mock_openai_cls):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Structured answer"
        mock_response.usage.prompt_tokens = 20
        mock_response.usage.completion_tokens = 8
        mock_response.usage.total_tokens = 28

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        provider = OpenAIProvider(
            model_name="openai/gpt-oss-20b",
            api_key=api_key,
            base_url=base_url
        )

        result = provider.generate(
            prompt="Return JSON",
            system_prompt="You are a strict JSON assistant."
        )

        mock_client.chat.completions.create.assert_called_once_with(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are a strict JSON assistant."},
                {"role": "user", "content": "Return JSON"},
            ],
        )

        assert result["content"] == "Structured answer"
        assert result["usage"]["total_tokens"] == 28
        assert result["provider"] == "openai"

    @patch("src.core.openai_provider.OpenAI")
    def test_stream_without_system_prompt(self, mock_openai_cls):
        # Mock streaming chunks
        chunk1 = Mock()
        chunk1.choices = [Mock()]
        chunk1.choices[0].delta.content = "Hello"

        chunk2 = Mock()
        chunk2.choices = [Mock()]
        chunk2.choices[0].delta.content = " world"

        chunk3 = Mock()
        chunk3.choices = [Mock()]
        chunk3.choices[0].delta.content = None  # ignored

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = [chunk1, chunk2, chunk3]
        mock_openai_cls.return_value = mock_client

        provider = OpenAIProvider(
            model_name="openai/gpt-oss-20b",
            api_key="fake-key",
            base_url="https://fake-url.com/v1"
        )

        output = list(provider.stream("Say hello"))

        mock_client.chat.completions.create.assert_called_once_with(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": "Say hello"}],
            stream=True
        )

        assert output == ["Hello", " world"]

    @patch("src.core.openai_provider.OpenAI")
    def test_stream_with_system_prompt(self, mock_openai_cls):
        chunk1 = Mock()
        chunk1.choices = [Mock()]
        chunk1.choices[0].delta.content = "Part 1"

        chunk2 = Mock()
        chunk2.choices = [Mock()]
        chunk2.choices[0].delta.content = " Part 2"

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = [chunk1, chunk2]
        mock_openai_cls.return_value = mock_client

        provider = OpenAIProvider(
            model_name="openai/gpt-oss-20b",
            api_key=api_key,
            base_url=base_url
        )

        output = list(provider.stream(
            prompt="Write something",
            system_prompt="You are helpful."
        ))

        mock_client.chat.completions.create.assert_called_once_with(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Write something"},
            ],
            stream=True
        )

        assert output == ["Part 1", " Part 2"]