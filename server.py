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
        self.cli_active = False
        self.setup_routes()
        self.commands_completer = WordCompleter(['help', 'start', 'stop', 'status'], ignore_case=True)
        self.style = Style.from_dict({
            'prompt': 'fg:#008000 bold',  # Green bold
            'message': 'fg:#00ffff italic',  # Cyan italic
            'response': 'fg:#ffff00',  # Bright yellow
            'info': 'fg:#ffffff bg:#606060',  # White on grey background
        })

    def setup_routes(self):
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.clients.append(websocket)
            logging.info("Client connected")
            if not self.cli_active:
                await self.manage_cli()
            try:
                while True:
                    response = await websocket.receive_text()
                    logging.info(f"Received response: {response}")
                    # Process the response or echo it back to clients
                    for client in self.clients:
                        if client is not websocket:
                            await client.send_text(f"Echo: {response}")
            except WebSocketDisconnect:
                self.clients.remove(websocket)
                logging.info("Client disconnected")
                if not self.clients:
                    self.cli_active = False
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                self.clients.remove(websocket)

    async def cli_input_loop(self):
        self.cli_active = True
        session = PromptSession(style=self.style, completer=self.commands_completer)
        with patch_stdout():
            while self.clients:
                try:
                    message = await session.prompt_async('Enter a command to send: ')
                    for client in self.clients:
                        await client.send_text(message)
                        logging.info(f"Sent message to client: {message}")
                except Exception as e:
                    logging.error(f"CLI Error: {e}")
                    break
        self.cli_active = False

    async def manage_cli(self):
        if self.clients and not self.cli_active:
            loop = asyncio.get_event_loop()
            await loop.create_task(self.cli_input_loop())

if __name__ == "__main__":
    server = WebSocketServer()
    import uvicorn
    config = uvicorn.Config(app=server.app, host="0.0.0.0", port=8000, lifespan="on")
    server_instance = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server_instance.serve())
