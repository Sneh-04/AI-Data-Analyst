import os
from abc import ABC, abstractmethod

import httpx
from openai import OpenAI


class LLMProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    @abstractmethod
    def generate(self, prompt: str, context: str) -> str:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        self.client = OpenAI(api_key=api_key)
        self.embedding_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        self.generate_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.embedding_model, input=text)
        return response.data[0].embedding

    def generate(self, prompt: str, context: str) -> str:
        response = self.client.chat.completions.create(
            model=self.generate_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer only from the supplied dataset context. If the context is insufficient, "
                        "say so. Do not invent values or rows. Return a concise natural-language answer."
                    ),
                },
                {"role": "user", "content": f"Dataset context:\n{context}\n\nQuestion: {prompt}"},
            ],
        )
        return response.choices[0].message.content or "I couldn't generate an answer."


class OllamaProvider(LLMProvider):
    def __init__(self) -> None:
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.embedding_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        self.generate_model = os.getenv("OLLAMA_GENERATE_MODEL", "llama3.1")

    def embed(self, text: str) -> list[float]:
        response = httpx.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.embedding_model, "prompt": text},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["embedding"]

    def generate(self, prompt: str, context: str) -> str:
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.generate_model,
                "prompt": (
                    "Answer only from the supplied dataset context. If the context is insufficient, "
                    "say so. Do not invent values or rows. Return a concise natural-language answer.\n\n"
                    f"Dataset context:\n{context}\n\nQuestion: {prompt}"
                ),
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "I couldn't generate an answer.")


def get_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "openai":
        return OpenAIProvider()
    if provider == "ollama":
        return OllamaProvider()
    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
