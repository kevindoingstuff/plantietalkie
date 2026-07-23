
from langchain.tools import BaseTool
import os 
from pathlib import Path
from langchain.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.tools import tool
from typing import Type

load_dotenv()

#Find root directory
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parents[2]

class LightIntensityInput(BaseModel):
    intensity: int = Field(description="The level of light intensity currently in the room.")
    optimal_intensity: int = Field(description="The optimal light intensity level for the plant in the room.")

class LightIntensityTool(BaseTool):
    name = "LightIntensityAdjuster"
    description = "A tool to adjust the light intensity in a room to optimize and maintain light levels for plants."
    args_schema: Type[BaseModel] = LightIntensityInput

    def adjust_light_intensity(self, intensity: int, optimal_intensity: int) -> str:
        """
        Adjust the light intensity in a room to optimize and maintain light levels for plants.
        
        Args:
        intensity: The level of light intensity currently in the room. 
        optimal_intensity: The optimal light intensity level for the plant in the room.
        
        Returns:
        The adjusted optimized light level
        """
        bulb_intensity = optimal_intensity - intensity
        if intensity < optimal_intensity:
            return f"Light intensity adjusted to {optimal_intensity}Lux by turning the light on to {bulb_intensity}Lux."
        else:
            return f"Light intensity does not need to be adjusted. Current intensity is {intensity}."

    def _run(self, intensity: int, optimal_intensity: int) -> str:
        return self.adjust_light_intensity(intensity, optimal_intensity)