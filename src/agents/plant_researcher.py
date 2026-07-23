import sys
import os
from pathlib import Path
from typing import List, Optional, Union, Literal, Dict, Any, Optional

# Set up project paths
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parents[2]
sys.path.append(str(project_root))

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, BaseMessage
from langchain.tools import BaseTool
from langgraph.graph import StateGraph, START, END
import json
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.agents import AgentActionMessageLog, AgentFinish
from langchain.agents.format_scratchpad import format_to_openai_function_messages

from src.models.open_ai import SQLOpenAILLM
from src.tools.LightIntensityTool import LightIntensityTool


class TaskAgentInput(BaseModel):
    input: str = Field(description="The output of the last stage")

class TaskAgentOutput(BaseModel):
    messages: List[BaseMessage] = Field(description="The messages to be displayed to the user")
    tools_used: List[Optional[str]] = Field(description="The tools used by the agent")

def parse(output):
    if "function_call" not in output.additional_kwargs:
        # Normalize plain-text finishes to the same shape as TaskAgentOutput
        return AgentFinish(
            return_values={"messages": [{"content": output.content}], "tools_used": []},
            log=output.content,
        )

    function_call = output.additional_kwargs["function_call"]
    name = function_call["name"]
    inputs = json.loads(function_call["arguments"])

    if name == "TaskAgentOutput":
        return AgentFinish(return_values=inputs, log=str(function_call))
    else:
        return AgentActionMessageLog(
            tool=name, tool_input=inputs, log="", message_log=[output]
        )

def create_task_agent(
    tools: List[BaseTool],
    llm: SQLOpenAILLM,
    agent_type: Optional[Union[Literal["tool-calling"], str]] = "tool-calling",
    verbose: bool = True,
    **kwargs: Any,
) -> AgentExecutor:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are a plant researcher tasked with analyzing plant data and determining maintenance actions. Follow these steps:

            1. Parse the SQL query results provided in the input.
            2. If a plant image is mentioned anywhere in the history, use the PlantIdentifierTool to identify the plant species and determine the optimal light intensity.
            3. Analyze the moisture level and compare it with the threshold (if provided in the input).
            3.5. If a task was mentioned in the input, eg. watering, only do that given task and ignore steps 4-6. 
            4. Use the WaterPumpTool to activate watering if the moisture level is below the threshold.
            5. Compare the current light intensity (if provided) with the optimal light intensity.
            6. Use the LightIntensityTool to adjust the light if necessary.
            7. Summarize the actions taken and provide recommendations.

            Notes:
            - Ensure all light intensity values are in Lux.
            - Utilize the time column from the data if available to decide on maintenance.
            - Adjust light intensity to safer values if the plant's health is compromised.
            - Execute tools asynchronously when possible for efficiency.
            - Do not use the same tool more than once for the same plant. 
            - Output a complete summary of actions and recommendations at the end.
            - Make the output in markdown format and friendly for chatbot responses"""),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    llm_with_tools = llm.bind_functions(tools + [TaskAgentOutput])

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
        }
        | prompt
        | llm_with_tools
        | parse
    )

    return AgentExecutor(
        name="Task Agent Executor",
        agent=agent,
        tools=tools,
        verbose=verbose,
        **kwargs,
    )