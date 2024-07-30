from langchain_google_genai import ChatGoogleGenerativeAI

class SQLGeminiLLM(ChatGoogleGenerativeAI):
    def __init__(self, **kwargs):
        super().__init__(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            **kwargs
        )
