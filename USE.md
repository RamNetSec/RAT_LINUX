# Instructivo de Uso del Centro de Comando WebSocket

## Descripción General

Este instructivo explica cómo utilizar el Centro de Comando WebSocket, un proyecto que permite la comunicación en tiempo real entre un servidor y múltiples clientes mediante WebSockets. Este proyecto permite ejecutar comandos de manera remota, transferir archivos y mantener una conexión persistente tanto en sistemas Windows como Linux.

## Requisitos Previos

- Python 3 instalado en el servidor y en los clientes.
- Acceso a la terminal en los sistemas donde se desplegará el servidor y los clientes.
- Los siguientes paquetes de Python instalados, los cuales se encuentran en el archivo `requirements.txt`:
  - `asyncio`
  - `websockets`
  - `subprocess`
  - `logging`
  - `fastapi`
  - `uvicorn`
  - `prompt_toolkit`

## Instalación

1. Clona el repositorio del proyecto:

    ```bash
    git clone https://github.com/RamNetSec/RAT_LINUX
    cd RAT_LINUX
    ```

2. Instala las dependencias necesarias:

    ```bash
    pip install -r requirements.txt
    ```

## Uso del Servidor

El servidor es responsable de administrar las conexiones de los clientes y enviarles comandos o solicitudes de transferencia de archivos.

1. Inicia el servidor con el siguiente comando:

    ```bash
    python server.py
    ```

2. Al ejecutar el servidor, se abrirá una CLI interactiva donde podrás ingresar comandos para los clientes conectados. Podrás:
    - Enviar comandos para ser ejecutados por los clientes.
    - Solicitar o enviar archivos utilizando los comandos "UPLOAD <nombre_del_archivo>" y "DOWNLOAD <nombre_del_archivo>".

## Uso del Cliente

El cliente debe ser ejecutado en los dispositivos que desees controlar de forma remota. El cliente se conectará al servidor y esperará comandos que le sean enviados.

1. Inicia el cliente con el siguiente comando:

    ```bash
    python client.py
    ```

2. El cliente se conectará al servidor especificado. Si la conexión se pierde, intentará reconectarse automáticamente cada dos segundos.

3. El cliente configurará automáticamente la persistencia para ejecutarse al inicio del sistema:
    - En **Windows**, copiará el script al directorio de inicio.
    - En **Linux**, agregará una tarea en `cron` para ejecutarse al inicio.

## Ejecución de Comandos

El servidor puede enviar comandos a los clientes conectados. La forma en que se ejecutan los comandos depende del sistema operativo:

- **Windows**: Los comandos se ejecutan utilizando PowerShell.
- **Linux**: Los comandos se ejecutan en el shell por defecto del sistema.

Para ejecutar comandos, simplemente escribe el comando en la CLI del servidor una vez que el cliente esté conectado. El resultado del comando será devuelto al servidor y mostrado en la consola.

## Transferencia de Archivos

- **Subir Archivos** (del servidor al cliente): Usa el comando `UPLOAD <nombre_del_archivo>`. El servidor enviará el archivo al cliente, quien lo guardará localmente.
- **Descargar Archivos** (del cliente al servidor): Usa el comando `DOWNLOAD <nombre_del_archivo>`. El cliente enviará el archivo solicitado al servidor.

Los archivos se transfieren de manera codificada utilizando Base64, lo cual permite la transferencia de cualquier tipo de archivo.

## Persistencia del Cliente

El cliente está diseñado para configurarse automáticamente para ejecutarse al inicio del sistema, asegurando su persistencia.

- **Windows**: El script se copia al directorio de inicio del sistema (`Startup`), garantizando que se ejecute cada vez que el sistema se inicie.
- **Linux**: Se agrega una entrada al cron para ejecutar el script al reiniciar el sistema.

Esta característica asegura que el cliente permanezca activo incluso después de reiniciar el equipo.

## Seguridad

Este proyecto permite ejecutar comandos remotos y transferir archivos, lo cual presenta ciertos riesgos de seguridad. Se recomienda:
- Ejecutar este software en un entorno controlado para pruebas o administración de sistemas.
- Proteger el acceso al servidor y a los clientes, ya que cualquier persona con acceso a la CLI del servidor podría controlar los clientes conectados.

## Resolución de Problemas

- **Conexión Cerrada**: Si el cliente pierde la conexión, intentará reconectarse automáticamente cada dos segundos. Verifica que el servidor esté en ejecución y que no existan bloqueos en la red.
- **Error en la Transferencia de Archivos**: Asegúrate de que el archivo solicitado exista y que tengas permisos adecuados para acceder a él.
- **Problemas de Persistencia**: Verifica que el script tenga los permisos necesarios para copiarse en el directorio de inicio en Windows o para editar el cron en Linux.

## Notas Finales

Este Centro de Comando WebSocket es una herramienta poderosa para la administración remota de sistemas, proporcionando funcionalidades de ejecución de comandos y transferencia de archivos. Sin embargo, debido a su capacidad de controlar sistemas de forma remota, debe ser utilizado con responsabilidad y únicamente en entornos donde se tenga permiso explícito para su uso.

