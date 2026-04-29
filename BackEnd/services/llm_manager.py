import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


class LLMManager:
    def __init__(self):
        # Default to 'ollama' if LLM_PROVIDER is not set
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    def get_llm(self):
        if self.provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            return ChatGoogleGenerativeAI(
                model="gemini-3-flash-preview", temperature=0, google_api_key=api_key
            )
        else:
            # Fallback to Ollama
            model_name = os.getenv("OLLAMA_MODEL", "phi3:mini")
            return ChatOllama(model=model_name, temperature=0)
