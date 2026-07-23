import os
import asyncio
import threading

from flask import Flask, request, jsonify
from flask_cors import CORS

from src.agents.simplified_sql_agent import PlantieTalkie
from src.tools.WaterPumpTool import WaterPumpTool
from src.tools.LightIntensityTool import LightIntensityTool
from src.tools.PlantDetectTool import PlantIdentifierTool

app = Flask(__name__)
CORS(app, origins=os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000").split(","))

MAX_INPUT_LENGTH = 2000

plantie_talkie = None
water_pump_tool = None
light_intensity_tool = None
plant_identifier_tool = None
models_initialized = False
_init_lock = threading.Lock()

def initialize_models():
    global plantie_talkie, water_pump_tool, light_intensity_tool, plant_identifier_tool, models_initialized
    with _init_lock:
        if not models_initialized:
            print("Initializing models...")
            plant_identifier_tool = PlantIdentifierTool()
            water_pump_tool = WaterPumpTool()
            light_intensity_tool = LightIntensityTool()
            plantie_talkie = PlantieTalkie()
            models_initialized = True
            print("Model initialization complete.")

@app.before_request
def before_request():
    initialize_models()

@app.route('/api/plantie_talkie', methods=['POST'])
def plantie_talkie_query():
    data = request.get_json(silent=True) or {}
    user_input = data.get('user_input')
    if not user_input or not isinstance(user_input, str):
        return jsonify({"error": "No user input provided"}), 400
    if len(user_input) > MAX_INPUT_LENGTH:
        return jsonify({"error": f"Input too long (max {MAX_INPUT_LENGTH} characters)"}), 400

    response, tools_used = asyncio.run(plantie_talkie.process_input(user_input))
    return jsonify({"response": response, "tools": tools_used})

@app.route('/api/water_plant', methods=['POST'])
def water_plant():
    data = request.get_json(silent=True) or {}
    plant_id = data.get('plant_id')
    if not plant_id:
        return jsonify({"error": "No plant ID provided"}), 400

    try:
        moisture_level = int(data.get('moisture_level', 50))
    except (TypeError, ValueError):
        return jsonify({"error": "moisture_level must be a number"}), 400
    moisture_level = max(0, min(100, moisture_level))

    result = water_pump_tool.activate_water_pump(plant_id, moisture_level)
    return jsonify({"message": result})

@app.route('/api/adjust_light', methods=['POST'])
def adjust_light():
    data = request.get_json(silent=True) or {}
    intensity = data.get('intensity')
    if intensity is None:
        return jsonify({"error": "No intensity provided"}), 400

    # Simulated current reading until a real sensor is wired up
    result = light_intensity_tool.adjust_light_intensity(1500, intensity)
    return jsonify({"message": result})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    # Log retrieval not implemented yet; shape is {timestamp, level, message}
    return jsonify([])

if __name__ == '__main__':
    initialize_models()
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
