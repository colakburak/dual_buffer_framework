# Dual Buffer System Application

This application demonstrates a real-time data processing system using a WebSocket connection between a client and a server. The server streams data over WebSockets, and the client processes this data using a dual buffer system.

## Directory Structure

- `./stream-the-data/`: Contains the server-side code.
- `./dual_buffer`: Contains the client-side code.

## Server-Side Setup (`./stream-the-data`)

The server is set up using FastAPI and streams data to clients over a WebSocket connection.

### Prerequisites

- Python 3.x
- FastAPI
- Uvicorn
- Numpy

### Running the Server

1. Navigate to the `stream-the-data` directory.
2. Install dependencies: `pip install -r requirements.txt` (if available).
3. Navigate to the `dataset/SMD` directory.
4. Unzip everything in the `SMD_dataset.zip`.
5. Run the server: `python main.py`.

The server listens on all network interfaces (`0.0.0.0`) at port `8000`.

## Client-Side Setup (`./dual_buffer`)

The client connects to the server over WebSocket and processes the incoming data using a dual buffer system.

### Prerequisites

- Python 3.x
- Websockets library

### Running the Client

1. Navigate to the `dual_buffer` directory.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the client: `python main.py`.

The client connects to `127.0.0.1:8000` (or `localhost:8000`) to receive data from the server.

## Networking Concepts

- **Server Address `0.0.0.0`**: The server listens on `0.0.0.0`, which means it's accessible from any IP address the machine has, making it suitable for testing across different network interfaces.

- **Client Address `127.0.0.1` or `localhost`**: The client uses `127.0.0.1` (or `localhost`) to connect to the server when running on the same machine. This loopback address is used for local testing and development.

## Contribution

Feel free to contribute to the project by submitting pull requests or issues.