from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
import logging

logging.basicConfig(level=logging.INFO)

class WebSocketServer:
    def __init__(self, host='0.0.0.0', port=8000):
        self.app = FastAPI()
        self.clients = []
        self.host = host
        self.port = port
        self.setup_routes()
        self.commands_completer = WordCompleter(['help', 'start', 'stop', 'status'], ignore_case=True)
        self.style = Style.from_dict({
            'prompt': 'fg:#008000 bold',
            'message': 'fg:#00ffff italic',
            'response': 'fg:#ffff00',
            'info': 'fg:#ffffff bg:#606060',
        })
        self.cli_task = None  # This will hold our CLI task

    def setup_routes(self):
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.clients.append(websocket)
            logging.info("Client connected")
            if len(self.clients) == 1:  # If first client, start CLI
                self.cli_task = asyncio.create_task(self.cli_input_loop())
            try:
                while True:
                    data = await websocket.receive_text()
                    logging.info(f"Received data: {data}")
            except WebSocketDisconnect:
                self.clients.remove(websocket)
                logging.info("Client disconnected")
                if not self.clients:  # If last client, stop CLI
                    self.cli_task.cancel()
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                self.clients.remove(websocket)
                if not self.clients:  # If last client, stop CLI
                    self.cli_task.cancel()

    async def cli_input_loop(self):
        session = PromptSession(style=self.style, completer=self.commands_completer)
        with patch_stdout():
            while True:
                try:
                    message = await session.prompt_async('Enter a command to send: ')
                    for client in self.clients:
                        await client.send_text(message)
                        logging.info(f"Sent message to client: {message}")
                except asyncio.CancelledError:
                    logging.info("CLI loop cancelled")
                    break
                except Exception as e:
                    logging.error(f"CLI Error: {e}")

if __name__ == "__main__":
    server = WebSocketServer()
    import uvicorn
    config = uvicorn.Config(app=server.app, host="0.0.0.0", port=8000, lifespan="on")
    server_instance = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server_instance.serve())
