from collections import deque
import threading
import asyncio
import websockets
import json

class DualBufferSystem:
    def __init__(self, window_size, processing_function, ws_conn_uri):
        self.active_buffer = deque()
        self.processing_buffer = deque()
        self.window_size = window_size  # This now represents the total number of data points before switching
        self.current_size = 0  # Track the current size of data points in the active buffer
        self.processing_function = processing_function
        self.ws_conn_uri = ws_conn_uri
        self.process_event = threading.Event()
        self.lock = threading.Lock()
        self.data_ingestion_thread = threading.Thread(target=self.run_ingest_data)
        self.processing_thread = threading.Thread(target=self.process_data)

    def start(self):
        self.data_ingestion_thread.start()
        self.processing_thread.start()

    def run_ingest_data(self):
        asyncio.run(self.ingest_data())

    async def ingest_data(self):
        async with websockets.connect(self.ws_conn_uri) as websocket:
            # Construct and send the 'start' command
            start_command = json.dumps({
                "command": "start",
                # Include any other necessary parameters for the 'start' command
                # TODO
                "batch_size": 100,  # Example parameter
                "start_index": 0,   # Example parameter
            })
            await websocket.send(start_command)

            # Optional: Wait for an acknowledgment from the server
            # ack = await websocket.recv()
            # if json.loads(ack).get("status") != "ok":
            #     print("Failed to start data transmission.")
            #     return

            while True:
                data = await websocket.recv()  # Assume data is a batch
                data_batch = self.parse_data(data)  # Parse batch of data

                with self.lock:
                    self.active_buffer.append(data_batch)
                    self.current_size += len(data_batch)  # Update the cumulative size

                    if self.current_size >= self.window_size:
                        self.switch_buffers()
                        self.process_event.set()  # Signal processing thread

    def process_data(self):
        while True:
            self.process_event.wait()
            self.process_event.clear()

            with self.lock:
                if self.processing_buffer:
                    self.processing_function(self.processing_buffer)
                    self.processing_buffer.clear()
                    self.current_size = 0  # Reset the size counter for the active buffer

    def switch_buffers(self):
        self.active_buffer, self.processing_buffer = self.processing_buffer, self.active_buffer
        # Reset the cumulative size of the active buffer
        self.current_size = sum(len(batch) for batch in self.active_buffer)

    @staticmethod
    def parse_data(data):
        import json
        try:
            parsed_data = json.loads(data)
        except json.JSONDecodeError:
            parsed_data = None
        return parsed_data

    def shutdown(self):
        if self.data_ingestion_thread.is_alive():
            self.data_ingestion_thread.join()

        with self.lock:
            if self.active_buffer:
                self.processing_function(self.active_buffer)
                self.active_buffer.clear()

        if self.processing_thread.is_alive():
            self.processing_thread.join()
