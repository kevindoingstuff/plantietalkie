import streamlit as st

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter

from dotenv import load_dotenv
import os
load_dotenv()
google_api_key = os.environ["GOOGLE_API_KEY"]
os.environ["LANGSMITH_TRACING"] = "true"
user_agent = os.environ.get('USER_AGENT')
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that provides detailed information of a stock token, {stock_token}.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm
message = chain.invoke(
    {
        "stock_token": "TSLA",
        "input": "What is the breakdown of the latest 10-K filing?",
    }
)

print(message.content)