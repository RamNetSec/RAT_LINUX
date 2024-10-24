# Servidor (Remote Control)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
import logging
import uvicorn
import os
import base64

# Configuración de logging con salto de línea antes de cada mensaje para claridad
logging.basicConfig(level=logging.INFO, format='\n%(asctime)s - %(levelname)s - \n%(message)s')

class WebSocketServer:
    def __init__(self, host='0.0.0.0', port=8000):
        self.app = FastAPI()
        self.clients = set()
        self.host = host
        self.port = port
        self.setup_routes()

        self.commands_completer = WordCompleter(
            ['help', 'UPLOAD', 'DOWNLOAD'],  # Comandos permitidos
            ignore_case=True
        )

        self.style = Style.from_dict({
            'prompt': 'fg:ansibrightgreen bold',    # Verde brillante y negrita para el prompt
            'message': 'fg:ansicyan italic',        # Cian y cursiva para los mensajes
            'response': 'fg:ansiyellow',            # Amarillo para las respuestas
            'info': 'fg:ansiwhite bg:ansiblack',    # Texto blanco sobre fondo negro para información
        })

        self.cli_task = None  # Esta variable contendrá nuestra tarea CLI

    def setup_routes(self):
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.clients.add(websocket)
            logging.info("Client connected\nINFO:     connection open")

            if self.cli_task is None or self.cli_task.done():  # Iniciar el CLI si no está ya en ejecución
                self.cli_task = asyncio.create_task(self.cli_input_loop())

            try:
                while True:
                    data = await websocket.receive_text()
                    logging.info(f"\nReceived data:\n{data}")
            except WebSocketDisconnect:
                self.clients.remove(websocket)
                logging.info("Client disconnected")
                if not self.clients:  # Si es el último cliente, detiene el CLI
                    self.cli_task.cancel()
            except (asyncio.TimeoutError, asyncio.CancelledError) as e:
                logging.error(f"\nAsync error:\n{str(e)}")
                self.clients.remove(websocket)
                if not self.clients:
                    self.cli_task.cancel()
            except Exception as e:
                logging.error(f"\nUnexpected error:\n{str(e)}")
                self.clients.remove(websocket)
                if not self.clients:
                    self.cli_task.cancel()

    async def cli_input_loop(self):
        session = PromptSession(style=self.style, completer=self.commands_completer)

        with patch_stdout():
            while True:
                try:
                    message = await session.prompt_async('Enter a command to send: ')
                    if message.startswith("UPLOAD "):
                        _, filename = message.split(" ", 1)
                        if not os.path.exists(filename):
                            logging.error(f"\nFile {filename} not found.")
                            continue
                        with open(filename, "rb") as f:
                            file_data = f.read()
                        encoded_data = base64.b64encode(file_data).decode()
                        for client in self.clients:
                            await client.send_text(message)
                            await client.send_text(encoded_data)
                            logging.info(f"\nSent file {filename} to client.")
                    elif message.startswith("DOWNLOAD "):
                        for client in self.clients:
                            await client.send_text(message)
                            logging.info(f"\nRequested file download: {message}")
                    else:
                        for client in self.clients:
                            await client.send_text(message)
                            logging.info(f"\nSent message to client:\n{message}")
                except asyncio.CancelledError:
                    logging.info("CLI loop cancelled")
                    break
                except (OSError, ValueError) as e:
                    logging.error(f"\nCLI Error:\n{str(e)}")

if __name__ == "__main__":
    server = WebSocketServer()
    config = uvicorn.Config(app=server.app, host="0.0.0.0", port=8000, lifespan="on")
    server_instance = uvicorn.Server(config)
    asyncio.run(server_instance.serve())