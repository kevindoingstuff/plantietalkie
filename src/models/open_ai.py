from langchain_openai import ChatOpenAI

class ConversationalOpenAILLM(ChatOpenAI):
    def __init__(self, **kwargs):
        super().__init__(
            model="gpt-4o-mini",
            temperature=0,
            timeout=None,
            max_retries=2,
            **kwargs
        )

class SQLOpenAILLM(ChatOpenAI):
    def __init__(self, **kwargs):
        super().__init__(
            model="gpt-4o-mini",
            temperature=0,
            timeout=None,
            max_retries=2,
            **kwargs
        )

class TaskOpenAILLM(ChatOpenAI):
    def __init__(self, **kwargs):
        super().__init__(
            model="gpt-4o-mini",
            temperature=0,
            timeout=None,
            max_retries=2,
            **kwargs
        )