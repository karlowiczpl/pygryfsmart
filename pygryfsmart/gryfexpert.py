import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class GryfExpert:

    def __init__(self, api , host='127.0.0.1', port=8888):
        self.host = host
        self.port = port

        self.writer = None
        self.server = None
        self._enable = False
        self._api = api

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        _LOGGER.debug(f"Connected with: {addr}")
        self.writer = writer
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    _LOGGER.error(f"Client: {addr} stop connection")
                    break

                message = data.decode().strip() + "\n\r"
                _LOGGER.debug(f"message from {addr}: {message}")

                await self._api.send_data(message)
        except asyncio.CancelledError:
            _LOGGER.error(f"Client: {addr} stop connection")
        except Exception as e:
            _LOGGER.error(f"ocurred error from {addr}: {e}")
        finally:
            _LOGGER.debug(f"Closing connection with {addr}")
            writer.close()
            await writer.wait_closed()

    async def send_data(self , message):
        if self.writer:
            try:
                self.writer.write(message.encode())
                await self.writer.drain()
            except Exception as e:
                _LOGGER.error(f"Unable to send message: {message}, error: {e}")
            finally:
                return
        else:
            _LOGGER.error(f"No client is connected")

    async def stop_server(self):
        if self.server:
            _LOGGER.debug("Stopping the server")
            self.server.close()
            await self.server.wait_closed()
            _LOGGER.debug("Server stopped")
        else:
            _LOGGER.error("Server is not running")

        self._enable = False

    async def start_server(self):
        self._api.subscribe_input_message(self.send_data)
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )

        addr = self.server.sockets[0].getsockname()

        async with self.server:
            await self.server.serve_forever()

        self._enable = True

    @property
    def enable(self):
        return self._enable
