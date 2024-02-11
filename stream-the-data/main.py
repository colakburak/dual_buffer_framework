from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import asyncio

app = FastAPI()

# Setup CORS if needed
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
    total_data_points = len(data)
    try:
        #flag = 0
        for index, (input_data, label) in enumerate(zip(data, labels)):
            progress_percentage = (index / total_data_points) * 100
            # if progress_percentage != flag:
            print(f"Progress: {progress_percentage:.2f}%")
            # flag = progress_percentage
            # Send data as serialized string; adapt as needed for your client
            message = {"input_data": input_data.tolist(), "label": label.tolist()}
            await websocket.send_json(message)
            await asyncio.sleep(0.0005)  # simulate a delay
        await websocket.send_json({"finished": True})
    except WebSocketDisconnect:
        print("Client disconnected!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000, ws_ping_interval=1000000000000000000000, ws_ping_timeout=1000000000000000000000)
    uvicorn.run(app, host="0.0.0.0", port=8000, ws_ping_interval=None, ws_ping_timeout=None)

