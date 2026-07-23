import time
import google.generativeai as genai
from langchain.tools import BaseTool
from PIL import Image
from pathlib import Path
from typing import Type, Any
import os
from langchain.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv
# Find root directory
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parents[2]
from src.prompts.tool_prompts import plant_identifier_prompt
load_dotenv()


class IdentifierInput(BaseModel):
    image_path: str = Field(description="The path to the image file to identify the plant species in.")

class PlantIdentifierTool(BaseTool):
    name = "Plant_Identifier"
    description = "A tool for identifying plant species in images."
    version = "1.0"
    args_schema: Type[BaseModel] = IdentifierInput
    model: Any = None
    prompt: str = plant_identifier_prompt

    def __init__(self):
        super().__init__()
        self.model = self._initialize_model()

    def _initialize_model(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-pro-002", system_instruction=self.prompt)

    def identify_plant_species(self, image_path) -> str:
        sleep_time = 20  # crude rate limit for the Gemini free tier
        start = time.perf_counter()
        image = Image.open(image_path)
        response = self.model.generate_content([image])
        end = time.perf_counter()
        duration = end - start
        time.sleep(sleep_time - duration if duration < sleep_time else 0)
        return response.text

    def _run(self, image_path: str) -> str:
        image_path = (project_root / image_path).resolve()

        # Only allow images inside the project directory
        if not image_path.is_relative_to(project_root):
            raise ValueError(f"Image path escapes project directory: {image_path}")
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        return self.identify_plant_species(image_path)