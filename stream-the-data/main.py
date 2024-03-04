from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn

import numpy as np
import json

from tqdm import tqdm  # Import tqdm for the progress bar

app = FastAPI()

# Setup CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data
data = np.load("./dataset/SMD/SMD_test.npy")
labels = np.load("./dataset/SMD/SMD_test_label.npy")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    send_data = False  # Initially not sending data
    try:
        while True:
            # Wait for a message from the client
            data_request = await websocket.receive_text()
            request = json.loads(data_request)

            # Handle start command
            if request.get("command") == "start":
                send_data = True  # Set flag to start sending data
                batch_size = request.get("batch_size", 10)  # Default batch size
                start_index = request.get("start_index", 0)  # Default start index

                # Calculate total progress steps
                total_steps = (len(data) - start_index) // batch_size + \
                              (0 if (len(data) - start_index) % batch_size == 0 else 1)

                # Initialize the progress bar
                with tqdm(total=total_steps, desc="Sending data", unit="batch") as pbar:
                    # Send data in batches based on the client's request
                    for index in range(start_index, len(data), batch_size):
                        if not send_data:
                            break  # Stop sending if the flag is reset
                        input_batch = data[index:index + batch_size].tolist()
                        label_batch = labels[index:index + batch_size].tolist()
                        message = {
                            "input_data": input_batch,
                            "label": label_batch
                        }
                        await websocket.send_json(message)
                        await asyncio.sleep(0.0005)  # Simulate processing delay
                        pbar.update(1)  # Update progress bar

                if send_data:
                    # Indicate completion only if not stopped prematurely
                    await websocket.send_json({"finished": True})

            # Handle stop command if implemented in the future

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)