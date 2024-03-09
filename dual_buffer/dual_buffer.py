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
        self.buffer_id_counter = 0 

        self.buffer_state = BufferState.FILLING
        # self.processing_finished = True

        self.active_buffer = {'input_data': [], 'label': []}
        self.processing_buffer = {'input_data': [], 'label': []}
        # asyncio.create_task(self.trigger_buffer_switch()) 


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
                data = await websocket.recv()
                data = json.loads(data) 

                if data.get('finished'):   
                    self.logger.info("Received 'finished' signal from server")
                      
                    break

                async with self.lock:
                    self.active_buffer['input_data'].extend(data['input_data'])
                    self.active_buffer['label'].extend(data['label'])
                    await self.send_acknowledgment(websocket) 

                if len(self.active_buffer['input_data']) >= self.window_size:
                    await self.trigger_buffer_switch() 
            
            # await self.shutdown()
            # Server communication completed, now start buffer processing
            # self.processing_task = asyncio.create_task(self.process_data()) 

    async def process_data(self):
        # self.logger.info("Processing Started") 
        while True:
            await self.switch_event.wait() 
            self.switch_event.clear()
            async with self.lock:
                if self.buffer_state == BufferState.PROCESSING:
                    self.buffer_id_counter += 1
                    self.logger.info("Processing Buffer #%d", self.buffer_id_counter)
                    data_window = np.array(self.processing_buffer['input_data'])  # Ensure you copy the data
                    # ... (Your processing logic) ...

                    # Directly switch buffer states when processing is done
                    self.buffer_state = BufferState.FILLING 
                    self.processing_buffer, self.active_buffer = self.active_buffer, {'input_data': [], 'label': []} 
                    self.switch_event.set()  # Signal data ingestion task

    async def trigger_buffer_switch(self):
        async with self.lock:
            if self.buffer_state == BufferState.FILLING:
                self.buffer_state = BufferState.PROCESSING
                self.processing_buffer, self.active_buffer = self.active_buffer, {'input_data': [], 'label': []}
                self.switch_event.set()  # Signal processing task to start 

    async def send_acknowledgment(self, websocket):
        ack_message = {"command": "ACK"}
        await websocket.send(json.dumps(ack_message))

    async def shutdown(self):
        self.logger.info("Initiating shutdown")

        # Cancel tasks (with 'await' for clean termination)
        try:
            if isinstance(self.ingestion_task, asyncio.Task): 
                await self.ingestion_task.cancel()
        except asyncio.CancelledError:
            pass  # Task was already cancelled or completed

        try:
            if isinstance(self.processing_task, asyncio.Task):
                await self.processing_task.cancel()
        except asyncio.CancelledError:
            pass  # Task was already cancelled or completed

        # WebSocket closure (Assuming your websocket object is available)
        try:
            await self.websocket.close()  # Add graceful close code if provided by your WebSocket library 
        except AttributeError:
            pass  # In case the websocket object might not be accessible here