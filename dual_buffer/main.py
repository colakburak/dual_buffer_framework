import asyncio
import logging
from dual_buffer import DualBufferSystem
import time
async def my_processing_function(input, label):
    # Your actual processing logic with the data
    # time.sleep(0.05) # FOR TESTING ONLY
    pass

async def main():
    # Setup logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Configuration
    window_size = 100  # Adjust as needed
    websocket_uri = "ws://127.0.0.1:8000/ws"  # Replace with your WebSocket server URI

    # Create the dual buffer system
    buffer_system = DualBufferSystem(window_size, websocket_uri, processing_func=my_processing_function) 

    # Run until shutdown
    try:
        await asyncio.gather(buffer_system.ingestion_task, buffer_system.processing_task)
    except asyncio.CancelledError:
        logger.info("Tasks cancelled. Shutting down")
    finally:
        await buffer_system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
