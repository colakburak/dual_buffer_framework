from dual_buffer import DualBufferSystem
import asyncio

def process_data(processing_buffer):
    total_data_points = sum(len(batch) for batch in processing_buffer)
    print(f"Processing a total of {total_data_points} data points from {len(processing_buffer)} batches...")


def main():
    # WebSocket connection URI
    ws_conn_uri = "ws://127.0.0.1:8000/ws"

    # Initialize the DualBufferSystem with a window size of 100 data points
    dual_buffer_system = DualBufferSystem(window_size=100, processing_function=process_data, ws_conn_uri=ws_conn_uri)

    # Start the DualBufferSystem
    dual_buffer_system.start()

    # Run for a short period then shut down for demonstration purposes
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        dual_buffer_system.shutdown()


if __name__ == "__main__":
    main()