from langchain_community.utilities import SQLDatabase
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_community.vectorstores import FAISS

from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import create_sql_query_chain
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

import os
import sys
from pathlib import Path

current_script_path = Path(__file__).resolve()
project_root = current_script_path.parents[2]
sys.path.append(str(project_root))

from src.models.gemini import SQLGeminiLLM
from dotenv import load_dotenv
load_dotenv()
examples = [
    {
        "input": "List the sensor readings for plant 3?",
        "query": "SELECT * FROM monsterathai3",
    },
    {
        "input": "List the sensor readings for plant 2?",
        "query": "SELECT * FROM monsterathai2",
    },

    {
        "input": "How many hours were the temperature under 30 degrees for plant 2?",
        "query": "SELECT COUNT(*) FROM monsterathai2 WHERE temperature < 30"
    }
]
db_path = project_root / "data" / "database" / "plant.db"
db = SQLDatabase.from_uri(f'sqlite:///{db_path}' )
context = db.get_context()
llm = SQLGeminiLLM()
size = "Large"


example_prompt = PromptTemplate.from_template("User input: {input}\nSQL query: {query}")
prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="You are a SQLite expert. Given an input question, create a syntactically correct SQLite query to run. Unless otherwise specificed, do not return more than {top_k} rows.\n\nHere is the relevant table info: {table_info}\n\nBelow are a number of examples of questions and their corresponding SQL queries.",
    suffix="User input: {input}\nSQL query: ",
    input_variables=["input", "top_k", "table_info"],
)

if size == "small":
    chain = create_sql_query_chain(llm, db)
    prompt_with_context = chain.get_prompts()[0].partial(table_info=context["table_info"])
else:
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
        FAISS,
        k=5,
        input_keys=["input"],
    )
    prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix="You are a SQLite expert. Given an input question, create a syntactically correct SQLite query to run. Unless otherwise specificed, do not return more than {top_k} rows.\n\nHere is the relevant table info: {table_info}\n\nBelow are a number of examples of questions and their corresponding SQL queries.",
        suffix="User input: {input}\nSQL query: ",
        input_variables=["input", "top_k", "table_info"],
    )
    chain = create_sql_query_chain(llm, db, prompt)
    result = chain.invoke({"question": f"how many hours were the moisture levels under 50% for plant 3?"})
    print(result)