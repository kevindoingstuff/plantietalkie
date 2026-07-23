from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Type

class WaterPumpInput(BaseModel):
    plant_id: int = Field(description="The ID of the plant.")
    moisture_level: int = Field(description="The latest moisture level of the plant.")

class WaterPumpTool(BaseTool):
    name = "WaterPumpActivator"
    description = "A tool to activate the water pump for a specific plant based on its moisture level."
    args_schema: Type[BaseModel] = WaterPumpInput

    def activate_water_pump(self, plant_id: int, moisture_level: int) -> str:
        """
        Activate the water pump for a specific plant for a specific duration. Useful when you want to water the plants.
        
        Args:
        plant_id: The ID of the plant.
        moisture_level: The latest moisture level of the plant.
        
        Returns:
        A message indicating that the water pump has been activated for the plant.
        """
        # Scale the moisture level to a duration
        duration = (100 - moisture_level) / 100 * 10
        print(f"Water pump activated for plant {plant_id} for {duration} seconds.")
        return f"Water pump activated for plant {plant_id} for {duration} seconds."

    def _run(self, plant_id: int, moisture_level: int) -> str:
        return self.activate_water_pump(plant_id, moisture_level)