import asyncio
import websockets
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri

    async def connect(self):
        retry_count = 0
        while True:
            try:
                async with websockets.connect(self.uri) as websocket:
                    logging.info("Connected to the server")
                    await self.handle_messages(websocket)
            except websockets.ConnectionClosed:
                logging.error("Connection closed, retrying...")
                retry_count += 1
                if retry_count > 5:
                    logging.error("Maximum retry attempts reached, exiting...")
                    break
                await asyncio.sleep(5**retry_count)
            except Exception as e:
                logging.error(f"Error: {e}")
                break

    async def handle_messages(self, websocket):
        while True:
            command = await websocket.recv()
            logging.info(f"Executing command: {command}")
            result = subprocess.run(["bash", "-c", command], capture_output=True, text=True)
            await self.send_response(websocket, result)
    async def send_response(self, websocket, result):
        if result.stdout:
            await websocket.send(f"Output: {result.stdout}")
        if result.stderr:
            await websocket.send(f"Error: {result.stderr}")

    async def run(self):
        await self.connect()

if __name__ == "__main__":
    client = WebSocketClient("ws://localhost:8000/ws")
    asyncio.run(client.run())
