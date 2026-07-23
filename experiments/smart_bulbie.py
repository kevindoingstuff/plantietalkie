import asyncio
import logging
from pathlib import Path

from zigpy_znp.api import ZNP
from zigpy.application import ControllerApplication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_zigbee():
    try:
        device_path = "COM10"  # Replace with your device path or COM port

        # Initialize ZNP with the device path directly
        znp = ZNP(

        # Connect to the Zigbee device
        await znp.connect()
        logger.info("Connected to Zigbee device on COM port.")

        # Create a ControllerApplication
        app = ControllerApplication(znp)

        # Start the application and form a Zigbee network
        await app.startup(auto_form=True)
        logger.info("Zigbee network setup complete.")

        return app
    except AttributeError as ae:
        logger.error(f"AttributeError: {ae}")
    except FileNotFoundError as fnfe:
        logger.error(f"FileNotFoundError: {fnfe}")
    except Exception as e:
        logger.error(f"Unexpected error during Zigbee setup: {e}")

    return None

def main():
    try:
        asyncio.run(setup_zigbee())
    except Exception as e:
        logger.error(f"Failed to run setup_zigbee: {e}")

if __name__ == "__main__":
    main()