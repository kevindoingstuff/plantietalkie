from langchain.prompts import ChatPromptTemplate
from src.models.open_ai import ConversationalOpenAILLM
from typing import Dict, Any
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

class StructuredOutput(BaseModel):
    action: str = Field(description="Main action or query type")
    plant_identifier: str = Field(description="Plant IDs or characteristics")
    conditions: list[str] = Field(description="List of conditions")
    time_info: str = Field(description="Any time-related information")
    attributes: list[str] = Field(description="List of relevant plant attributes")
    additional_info: str = Field(description="Any other relevant details")

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert plant maintenance system interpreter. Your role is to analyze user queries about plant care and maintenance, and convert them into a structured format that can be easily used to generate SQL queries.

        Key points to consider:
        1. Identify the main action or query type (e.g., check status, update records, perform maintenance).
        2. Specify the plant(s) involved, either by ID or characteristics.
        3. Note any specific conditions or thresholds mentioned. If no conditions are mentioned, use the default values. under 50 percent for moisture level and under 9000 for light intensity.
        4. Highlight any time-related information.
        5. Mention any specific plant attributes of interest (e.g., moisture level, light intensity).
        6. Make sure to query the location of the plant (foreign key) for the room light intensity and effective light intensity.

        {format_instructions}

        Remember to include all relevant information from the user's query, but structure it in a way that facilitates SQL query generation."""),
    ("human", "{input}"),
    ("ai", "Based on the user's input, here's the structured format for SQL query generation:"),
    ("human", "Great. Now, please process this user query: {input}")
])

def create_input_parser(prompt: ChatPromptTemplate = prompt, llm = ConversationalOpenAILLM()):
    parser = JsonOutputParser(pydantic_object=StructuredOutput)
    return prompt.partial(format_instructions=parser.get_format_instructions()) | llm | parser