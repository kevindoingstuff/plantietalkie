import os
import sys
import json
import sqlite3
import asyncio
import operator
import logging

from pathlib import Path
from typing import Sequence, Dict, Any, Generator, Annotated, Tuple, List

from sqlalchemy import create_engine
from langchain.agents import AgentExecutor
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, StateGraph, START
from langchain_core.pydantic_v1 import BaseModel
from langchain_community.agent_toolkits.sql.base import create_sql_agent
# Set up project paths
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parents[2]
sys.path.append(str(project_root))

from src.agents.plant_researcher import create_task_agent
from src.chains.input_parser import create_input_parser
from src.models.open_ai import SQLOpenAILLM
from src.tools.PlantDetectTool import PlantIdentifierTool
from src.tools.WaterPumpTool import WaterPumpTool
from src.tools.LightIntensityTool import LightIntensityTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    tools_used: Annotated[List[str], operator.add]

class PlantieTalkie:
    def __init__(self, db_path: Path = None):
        self.db_path = Path(db_path) if db_path else project_root / "data" / "database" / "plant_monitoring.db"
        # Genuine read-only connection: LLM-generated SQL cannot modify the DB.
        engine = create_engine(
            "sqlite://",
            creator=lambda: sqlite3.connect(f"file:{self.db_path.as_posix()}?mode=ro", uri=True),
        )
        self.db = SQLDatabase(engine)

        self.llm = SQLOpenAILLM()
        self.sql_prompt = self._initialize_prompt()

        self.sql_agent_executor = self._create_sql_agent()
        self.task_executor = self._create_task_agent()
        self.task_agent_called = False
        self.input_parser = create_input_parser()

        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

    def _initialize_prompt(self) -> PromptTemplate:
        prompt = PromptTemplate.from_template(
            """User input: {input}
                SQL query: {query}. Do not include SQL code blockers or backslashes in responses.
                Query the relevant rows from the database and return the results in a structured JSON format.
                Do not perform any analysis or make any decisions based on the data.
                Just return the raw query results and the image path if it exists.

                Format:
                {{
                    "query_results": [
                        {{
                            "column1": value1,
                            "column2": value2,
                            ...
                        }},
                        ...
                    ],
                    "image_path": "path/to/image.jpg"
                }}"""
        )
        return prompt

    def _create_sql_agent(self) -> AgentExecutor:
        return create_sql_agent(
            llm=self.llm,
            db=self.db,
            verbose=True,
            agent_type="tool-calling",
            suffix=str(self.sql_prompt),
            extra_tools=[]
            # Ensure the agent supports async operations
        )

    def _create_task_agent(self) -> AgentExecutor:
        tools = [WaterPumpTool(), LightIntensityTool(), PlantIdentifierTool()]
        return create_task_agent(
            tools=tools,
            llm=self.llm,
            verbose=True,
        )

    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        workflow.add_node("input_parser", self.call_input_parser)
        workflow.add_node("sql_agent", self.call_sql_model)
        workflow.add_node("task_agent", self.call_task_model)
        workflow.add_edge(START, "input_parser")
        workflow.add_edge("input_parser", "sql_agent")
        workflow.add_edge("sql_agent", "task_agent")
        workflow.add_edge("task_agent", END)
        return workflow

    def reset_workflow(self):
        # Rebuild the workflow to reset its state
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        self.task_agent_called = False


    async def call_input_parser(self, state: AgentState) -> Dict[str, Any]:
        messages = state.messages
        response = await self.input_parser.ainvoke({"input": messages[-1].content})
        # Convert the response dict to a string
        response = json.dumps(response)
        logger.debug(f"Input parser response: {response}")
        return {"messages": [AIMessage(content=response)]}

    async def call_sql_model(self, state: AgentState) -> Dict[str, Any]:
        messages = state.messages
        parser_response = messages[-1].content
        response = await self.sql_agent_executor.ainvoke({"input": parser_response})
        return {"messages": [AIMessage(content=response["output"])]}

    async def call_task_model(self, state: AgentState) -> Dict[str, Any]:
        messages = state.messages
        sql_result = messages[-1].content
        human_message = messages[0].content
        combined_input = f"User query: {human_message}\nSQL result: {sql_result}"
        response = await self.task_executor.ainvoke({"input": combined_input})
        logger.debug(f"Task agent response: {response}")
        # The task agent finishes either with a TaskAgentOutput function call
        # ({"messages": [...]}), or with plain text ({"output": ...}).
        output = response.get("messages", response.get("output", ""))
        if isinstance(output, list):
            output = "\n".join(
                m.get("content", str(m)) if isinstance(m, dict) else str(m)
                for m in output
            )
        return {
            "messages": [AIMessage(content=str(output))],
            "tools_used": response.get("tools_used", [])
        }

    async def process_input(self, user_input: str) -> Tuple[str, List[str]]:
        try:
            event = await self.app.ainvoke({"messages": [HumanMessage(content=user_input)]})
            logger.debug(f"Received event: {event}")

            response = "I apologize, but I couldn't generate a response. Please try asking your question again."
            tools_used = []

            if isinstance(event, dict) and 'messages' in event:
                messages = event['messages']
                tools_used = event.get('tools_used', [])
                if messages and isinstance(messages[-1], AIMessage):
                    response = messages[-1].content
                    logger.debug(f"Full response: {response}")
                    logger.debug(f"Tools used: {tools_used}")
                else:
                    logger.warning("Unexpected message format in event")
            else:
                logger.warning("Unexpected event format")

            # Reset the workflow only if task_agent was called
            if self.task_agent_called:
                logger.debug("Resetting workflow as task_agent was called")
                self.reset_workflow()
            else:
                logger.debug("Not resetting workflow as task_agent was not called")

            return response, tools_used
        except Exception as e:
            logger.exception(f"An error occurred while processing input: {e}")
            # Reset the workflow even if an error occurred
            self.reset_workflow()
            return f"An error occurred: {str(e)}", []
"""
if __name__ == "__main__":
    model = PlantieTalkie()
    asyncio.run(model.process_input("Conduct maintenance on plant 2 if moisture level is below 40 percent. Plant image: 2.jpg"))

    """