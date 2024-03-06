# from dual_buffer import DualBufferSystem
# import asyncio
# import websockets

# def process_data(processing_buffer):
#     # Example processing that prints the total data points and batch count
#     total_data_points = sum(len(data) for data, _ in processing_buffer)
#     print(f"Processing a total of {total_data_points} data points from {len(processing_buffer)} batches...")


# def main():
#     # WebSocket connection URI
#     ws_conn_uri = "ws://127.0.0.1:8000/ws"

#     # Initialize the DualBufferSystem with a window size of 100 data points
#     dual_buffer_system = DualBufferSystem(window_size=100, processing_function=process_data, ws_conn_uri=ws_conn_uri)

#     # Start the DualBufferSystem
#     dual_buffer_system.start()

#     # Run for a short period then shut down for demonstration purposes
#     try:
#         asyncio.get_event_loop().run_forever()
#     except KeyboardInterrupt:
#         print("Shutting down...")
#         dual_buffer_system.shutdown()


# if __name__ == "__main__":
#     main()

# ----------------

import asyncio
from dual_buffer import DualBufferSystem

async def main():
    buffer_system = DualBufferSystem(window_size=100, ws_conn_uri="ws://127.0.0.1:8000/ws") 
    await asyncio.gather(
        buffer_system.ingestion_task,
        buffer_system.processing_task
    )

if __name__ == "__main__":
    print("Starting the ingestion and processing tasks concurrently")
    asyncio.run(main())

# import websockets
# import asyncio
# import json

# ws_conn_uri = "ws://127.0.0.1:8000/ws"

# lock = asyncio.Lock()
# window_size = 100
# processing_finished = True

# async def send_acknowledgment(websocket):
#         await websocket.send("ack")  # Send acknowledgment 

# async def ingest_data():
#     active_buffer = {'input_data': [], 'label': []}
#     processing_buffer = {'input_data': [], 'label': []}
#     async with websockets.connect(ws_conn_uri) as websocket:
#         print('connected to ws')
#         while True:
#             # Request data (if needed)
#             await websocket.send(json.dumps({"command": "start"}))  

#             data = await websocket.recv()
#             data = json.loads(data)

#             async with lock:
#                 active_buffer['input_data'].extend(data['input_data'])
#                 active_buffer['label'].extend(data['label'])

#             await send_acknowledgment(websocket)

#             # Consolidated buffer check
#             if len(active_buffer['input_data']) >= window_size and processing_finished:
#                 active_buffer, processing_buffer = processing_buffer, active_buffer
#                 print("some process")
#                 processing_buffer = {'input_data': [], 'label': []}
            
# asyncio.run(ingest_data())