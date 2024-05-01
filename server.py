from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
import logging

# Configuración de logging con salto de línea antes de cada mensaje para claridad
logging.basicConfig(level=logging.INFO, format='\n%(asctime)s - %(levelname)s - \n%(message)s')

class WebSocketServer:
    def __init__(self, host='0.0.0.0', port=8000):
        self.app = FastAPI()
        self.clients = []
        self.host = host
        self.port = port
        self.setup_routes()

        self.commands_completer = WordCompleter(
            ['help', 'start', 'stop', 'status'],
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
            self.clients.append(websocket)
            logging.info("Client connected\nINFO:     connection open")

            if len(self.clients) == 1:  # Si es el primer cliente, inicia el CLI
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
                    for client in self.clients:
                        await client.send_text(message)
                        logging.info(f"\nSent message to client:\n{message}")
                except asyncio.CancelledError:
                    logging.info("CLI loop cancelled")
                    break
                except Exception as e:
                    logging.error(f"\nCLI Error:\n{str(e)}")

if __name__ == "__main__":
    server = WebSocketServer()
    import uvicorn
    config = uvicorn.Config(app=server.app, host="0.0.0.0", port=8000, lifespan="on")
    server_instance = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server_instance.serve())
