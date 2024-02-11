from collections import deque
import threading
import asyncio
import websockets

class DualBufferSystem:
    def __init__(self, window_size, processing_function):
        self.active_buffer = deque(maxlen=window_size)
        self.processing_buffer = deque(maxlen=window_size)
        self.window_size = window_size
        self.processing_function = processing_function
        self.process_event = threading.Event()
        self.lock = threading.Lock()
        self.data_ingestion_thread = threading.Thread(target=self.ingest_data)
        self.processing_thread = threading.Thread(target=self.process_data)

    def start(self):
        self.data_ingestion_thread = threading.Thread(target=self.run_ingest_data)
        self.data_ingestion_thread.start()
        self.processing_thread.start()

    def run_ingest_data(self):
        asyncio.run(self.ingest_data())

    async def ingest_data(self):
        """
        Asynchronously listen to WebSocket and append data to the active buffer.
        If active_buffer size reaches window_size, switch buffers and signal processing.
        """
        async with websockets.connect('ws://127.0.0.1:8000/ws') as websocket:
            while True:
                data = await websocket.recv()  # Receive data from WebSocket
                data_point = self.parse_data(data)  # Parse data to desired format

                with self.lock:
                    self.active_buffer.append(data_point)

                    if len(self.active_buffer) == self.window_size:
                        self.switch_buffers()
                        self.process_event.set()  # Signal processing thread

    def process_data(self):
        """
        Continuously process data from the processing buffer.
        """
        while True:
            self.process_event.wait()  # Wait for signal from ingest_data
            self.process_event.clear()  # Clear the event after it's signaled

            with self.lock:
                if self.processing_buffer:
                    self.processing_function(self.processing_buffer)
                    self.processing_buffer.clear()

    def switch_buffers(self):
        """
        Swap roles of active_buffer and processing_buffer.
        """
        self.active_buffer, self.processing_buffer = self.processing_buffer, self.active_buffer

    @staticmethod
    def parse_data(data):
        """
        Parse the incoming WebSocket data into the desired format.
        """
        # Example: Assuming JSON input and converting it to a Python dictionary due to API Res.
        import json
        try:
            parsed_data = json.loads(data)
        except json.JSONDecodeError:
            parsed_data = None  # or some other value for err handling
        return parsed_data


    def shutdown(self):
        """
        Cleanly shut down the system, ensuring all buffers are processed.
        """
        # Stop the data ingestion thread
        if self.data_ingestion_thread.is_alive():
            self.data_ingestion_thread.join()

        # Process any remaining data in the active buffer
        with self.lock:
            if self.active_buffer:
                self.processing_function(self.active_buffer)
                self.active_buffer.clear()

        # Stop the processing thread
        if self.processing_thread.is_alive():
            self.processing_thread.join()
            