# Centro de Comando WebSocket

## Descripción General

Este proyecto es un Centro de Comando WebSocket basado en Python que permite la comunicación en tiempo real entre un servidor y múltiples clientes. Utiliza `asyncio`, `websockets`, `subprocess`, y `fastapi` para crear un entorno robusto e interactivo de ejecución de comandos a través de WebSockets. Además, permite la transferencia de archivos entre el servidor y los clientes y la persistencia en sistemas Windows y Linux.

## Características

- **Arquitectura de Servidor y Cliente**: Implementa tanto el servidor como el cliente WebSocket usando Python.
- **Ejecución de Comandos**: Ejecuta comandos recibidos vía WebSocket y devuelve la salida.
- **Transferencia de Archivos**: Permite subir y descargar archivos entre el servidor y los clientes.
- **Reconexión Automática**: El cliente intentará reconectarse en caso de pérdida de conexión.
- **Soporte CLI**: CLI interactivo para enviar comandos a los clientes conectados desde el servidor.
- **Persistencia Automática**: Configuración de persistencia para que el cliente se ejecute automáticamente al inicio en sistemas Windows y Linux.

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

El cliente intentará reconectarse automáticamente en caso de pérdida de conexión y establecerá persistencia en el sistema operativo para ejecutarse al inicio.
