from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn
import numpy as np
import json
from tqdm import tqdm

app = FastAPI()

# Setup CORS (unchanged)
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
    send_data = False
    try:
        while True:
            data_request = await websocket.receive_text()
            request = json.loads(data_request)

            if request.get("command") == "start":
                send_data = True 
                batch_size = request.get("batch_size", 10)   
                start_index = request.get("start_index", 0)

                total_steps = (len(data) - start_index) // batch_size + \
                          (0 if (len(data) - start_index) % batch_size == 0 else 1)

                with tqdm(total=total_steps, desc="Sending data", unit="batch") as pbar:
                    for index in range(start_index, len(data), batch_size):
                        if not send_data:
                            break

                        input_batch = data[index:index + batch_size].tolist()
                        label_batch = labels[index:index + batch_size].tolist()
                        message = {
                            "input_data": input_batch,
                            "label": label_batch
                        }
                        await websocket.send_json(message)
                        pbar.update(1) 

                        # Non-blocking acknowledgment check
                        try:
                            message_str = await asyncio.wait_for(websocket.receive_text(), timeout=10)
                            message = json.loads(message_str)
                            if message.get("command") != "ACK":
                                print(f"Unexpected acknowledgment message: {message}. Expected 'ACK' command")
                                # You might choose to handle this as an error condition 
                        except asyncio.TimeoutError:
                            print("Timeout, waiting for next batch request..")
                            break 

                # Indicate completion if we sent all batches
                if send_data:
                    await websocket.send_json({"finished": True})
                    break

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
