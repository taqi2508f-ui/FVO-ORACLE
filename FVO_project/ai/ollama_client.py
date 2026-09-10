import json
import os
import threading
from typing import Callable, Optional

import requests


GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "openai/gpt-oss-120b"


class GroqClient:
    """Small OpenAI-compatible Groq client with streaming and session key support."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = GROQ_BASE_URL,
        model: str = DEFAULT_MODEL,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()
        self._stop = threading.Event()

    def set_api_key(self, api_key: str):
        """Set a key for this app session without writing it to disk."""
        self.api_key = api_key.strip()

    def clear_api_key(self):
        self.api_key = ""

    def has_api_key(self) -> bool:
        return bool(self.api_key)

    def stop(self):
        self._stop.set()

    def reset(self):
        self._stop.clear()

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def is_available(self) -> tuple:
        """Return (api_reachable, selected_model_available, model_ids)."""
        if not self.api_key:
            return False, False, []

        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self._headers(),
                timeout=8,
            )
            if response.status_code != 200:
                return False, False, []

            models = [
                model.get("id", "")
                for model in response.json().get("data", [])
                if model.get("id")
            ]
            return True, self.model in models, models
        except (requests.RequestException, ValueError, TypeError):
            return False, False, []

    def chat_stream(
        self,
        prompt: str,
        system_prompt: str = "",
        on_token: Optional[Callable] = None,
        on_done: Optional[Callable] = None,
    ) -> str:
        self.reset()

        if not self.api_key:
            err = "[ERROR] Groq API key is missing. Click [GROQ API KEY] to add it."
            if on_token:
                on_token(err)
            if on_done:
                on_done(err)
            return err

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "temperature": 0.6,
                    "top_p": 0.95,
                    "max_completion_tokens": 12000,
                    "reasoning_effort": "medium",
                },
                stream=True,
                timeout=(10, 300),
            )
            response.raise_for_status()

            full_response = []
            done_called = False
            for raw_line in response.iter_lines(decode_unicode=True):
                if self._stop.is_set():
                    break
                if not raw_line:
                    continue

                line = raw_line if isinstance(raw_line, str) else raw_line.decode("utf-8")
                if not line.startswith("data:"):
                    continue

                payload = line[5:].strip()
                if payload == "[DONE]":
                    break

                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    continue

                choices = data.get("choices") or []
                delta = choices[0].get("delta", {}) if choices else {}
                token = delta.get("content") or ""
                if token:
                    full_response.append(token)
                    if on_token:
                        on_token(token)

            result = "".join(full_response)
            if on_done:
                on_done(result)
                done_called = True
            return result
        except requests.exceptions.ConnectionError:
            err = "[ERROR] Cannot connect to Groq. Check your internet connection."
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            if status in (401, 403):
                err = "[ERROR] Groq rejected the API key. Check the key and try again."
            else:
                err = f"[ERROR] Groq API request failed (HTTP {status})."
        except requests.RequestException as exc:
            err = f"[ERROR] Groq request failed: {exc}"
        except Exception as exc:
            err = f"[ERROR] {exc}"

        if on_token:
            on_token(err)
        if on_done and not done_called:
            on_done(err)
        return err

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        collected = []
        self.chat_stream(
            prompt,
            system_prompt=system_prompt,
            on_token=lambda token: collected.append(token),
        )
        return "".join(collected)


# Compatibility alias for code that imported the previous client name.
OllamaClient = GroqClient
