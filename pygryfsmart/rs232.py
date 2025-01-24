import logging
from serial_asyncio import open_serial_connection

_LOGGER = logging.getLogger(__name__)

class RS232Handler:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.reader = None
        self.writer = None

    async def open_connection(self):
        try:
            self.reader, self.writer = await open_serial_connection(url=self.port, baudrate=self.baudrate)
            _LOGGER.info(f"Connection opened on port {self.port} with baudrate {self.baudrate}")
        except Exception as e:
            _LOGGER.error(f"Failed to open connection on port {self.port}: {e}")
            self.reader, self.writer = None, None
            raise

    async def close_connection(self):
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
                _LOGGER.info("Connection closed successfully.")
            except Exception as e:
                _LOGGER.error(f"Error while closing connection: {e}")
        else:
            _LOGGER.warning("Connection was already closed or not initialized.")

    async def send_data(self, data):
        if self.writer:
            try:
                self.writer.write(data.encode())
                await self.writer.drain()
                _LOGGER.debug(f"Sent data: {data}")
            except Exception as e:
                _LOGGER.error(f"Error while sending data: {e}")
        else:
            _LOGGER.warning("Cannot send data: Writer is not initialized.")

    async def read_data(self):
        if self.reader:
            try:
                data = await self.reader.readuntil(b"\n")
                _LOGGER.debug(f"Read data: {data.decode().strip()}")
                return data.decode().strip()
            except Exception as e:
                _LOGGER.error(f"Error while reading data: {e}")
                return None
        else:
            _LOGGER.warning("Cannot read data: Reader is not initialized.")
            return None
