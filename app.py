import streamlit as st
import asyncio
import logging
from pathlib import Path
from io import StringIO
import sys

# Setup path for imports
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent
sys.path.append(str(project_root))

from src.agents.simplified_sql_agent import PlantieTalkie
from src.tools.WaterPumpTool import WaterPumpTool
from src.tools.LightIntensityTool import LightIntensityTool

# Configure logging
def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Create a StringIO object to capture log output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    return logger, log_stream

logger, log_stream = setup_logging()

# App configuration
st.set_page_config(page_title="PlantieTalkie", page_icon="🌿", layout="wide")

@st.cache_resource
def get_plantie_talkie():
    """Initialize and cache the PlantieTalkie agent instance."""
    return PlantieTalkie()

# Initialize components
plantie_talkie = get_plantie_talkie()

# UI Components
def render_chat_history():
    """Render the chat history from session state."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "tools" in message:
                st.caption(f"Tools used: {', '.join(message['tools'])}")

async def process_user_input(prompt: str):
    """Process user input and get response from PlantieTalkie."""
    try:
        response, tools_used = await plantie_talkie.process_input(prompt)
        full_response = response if isinstance(response, str) else str(response)

        logger.info(f"Response from PlantieTalkie: {full_response}")
        logger.debug(f"Tools used: {tools_used}")
        
        return full_response, tools_used
    except Exception as e:
        logger.exception(f"An error occurred processing input: {e}")
        return f"An error occurred: {str(e)}", []

def render_sidebar_controls():
    """Render the sidebar controls for manual plant operations."""
    st.sidebar.title("Manual Plant Controls")

    # Plant selection
    plant_id = st.sidebar.selectbox("Select Plant", [1, 2, 3, 4, 5])
    
    # Manual watering control
    st.sidebar.subheader("Water Control")
    if st.sidebar.button("Water Plant"):
        water_pump_tool = WaterPumpTool()
        result = water_pump_tool.activate_water_pump(plant_id, 50)
        st.sidebar.success(result)

    # Manual light intensity control
    st.sidebar.subheader("Light Control")
    optimal_intensity = st.sidebar.slider("Optimal Light Intensity (Lux)", 0, 10000, 1500)
    if st.sidebar.button("Adjust Light"):
        light_intensity_tool = LightIntensityTool()
        result = light_intensity_tool.adjust_light_intensity(1500, optimal_intensity)
        st.sidebar.success(result)

def main():
    """Main application function."""
    st.title("PlantieTalkie 🌿")

    # Initialize chat history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    render_chat_history()

    # Handle user input
    if prompt := st.chat_input("What would you like to know about your plants?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            full_response, tools_used = asyncio.run(process_user_input(prompt))
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response, 
                "tools": tools_used
            })
            
            if tools_used:
                st.caption(f"Tools used: {', '.join(tools_used)}")

    # Render sidebar controls
    render_sidebar_controls()

    # Debug logs section
    if st.checkbox("Show Debug Logs"):
        st.text_area("Debug Logs", value=log_stream.getvalue(), height=300)

if __name__ == "__main__":
    main()