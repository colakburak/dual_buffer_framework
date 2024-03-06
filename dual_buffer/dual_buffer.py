from enum import Enum
import asyncio
import numpy as np
import json
import websockets
import logging 

class BufferState(Enum):
    FILLING = 1 
    PROCESSING = 2
    SWITCHING = 3

class DualBufferSystem:
    def __init__(self, window_size, ws_conn_uri):
        self.window_size = window_size
        self.ws_conn_uri = ws_conn_uri  

        self.buffer_state = BufferState.FILLING
        self.processing_finished = True

        self.active_buffer = {'input_data': [], 'label': []}
        self.processing_buffer = {'input_data': [], 'label': []}
        asyncio.create_task(self.trigger_buffer_switch()) 


        self.lock = asyncio.Lock()
        self.switch_event = asyncio.Event()

        self.ingestion_task = asyncio.create_task(self.ingest_data())
        self.processing_task = asyncio.create_task(self.process_data())

        # Logger
        self.logger = logging.getLogger(__name__)  
        self.logger.setLevel(logging.DEBUG) 
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    async def ingest_data(self):
        self.logger.info("Attempting WebSocket connection") 
        async with websockets.connect(self.ws_conn_uri) as websocket:
            self.logger.info("Connected!")
            await websocket.send(json.dumps({"command": "start"}))
            while True:
                # Request data (if needed)
                # await websocket.send(json.dumps({"command": "start"}))  

                data = await websocket.recv()
                data = json.loads(data)  

                if data.get('finished'):  # Check for the 'finished' key
                    self.logger.info("Received 'finished' signal from server")
                    await self.shutdown()  # Initiate shutdown
                    break 

                async with self.lock:
                    self.active_buffer['input_data'].extend(data['input_data'])
                    self.active_buffer['label'].extend(data['label'])

                await self.send_acknowledgment(websocket)  

                # Consolidated buffer check
                if len(self.active_buffer['input_data']) >= self.window_size and self.processing_finished:
                    await self.trigger_buffer_switch()  

    async def process_data(self):
        while True:
            await self.switch_event.wait() 
            self.switch_event.clear()  # Clear after receiving the signal

            async with self.lock:
                if self.buffer_state == BufferState.PROCESSING:
                    self.logger.debug("Processing data from buffer with state: %s", self.buffer_state)
                    data_window = np.array(self.processing_buffer)
                    # ... (Your processing logic) ...

            self.processing_finished = True
            await self.trigger_buffer_switch() # Trigger a new switch after processing

    async def trigger_buffer_switch(self):
        async with self.lock:
            if self.buffer_state == BufferState.PROCESSING:  # Check if ready to switch
                self.buffer_state = BufferState.SWITCHING  # Temporarily mark as switching
                self.processing_buffer, self.active_buffer = self.active_buffer, {'input_data': [], 'label': []}
                self.buffer_state = BufferState.FILLING  # Reset state immediately
                self.switch_event.set()  # Signal processing task 

    async def send_acknowledgment(self, websocket):
        await websocket.send("ack")  # Send acknowledgment 

    async def shutdown(self):
        self.logger.info("Initiating shutdown")
        # self.ingestion_task.cancel()
        # self.processing_task.cancel()
        # ...
        try:
            self.ingestion_task.cancel()
        except asyncio.CancelledError:
            pass  # Ignore CancelledErrors during shutdown

        try:
            self.processing_task.cancel()
        except asyncio.CancelledError:
            pass 
        # ... (Potentially close WebSocket connections)