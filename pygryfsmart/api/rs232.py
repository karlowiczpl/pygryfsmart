from serial_asyncio import open_serial_connection
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)

class RS232Handler:
    def __init__(self, port, baudrate, reconnect_delay=5):
        self.port = port
        self.baudrate = baudrate
        self.reconnect_delay = reconnect_delay
        self.reader = None
        self.writer = None
        self._lock = asyncio.Lock()

    async def open_connection(self):
        async with self._lock:
            if self.writer:
                return
            try:
                self.reader, self.writer = await open_serial_connection(url=self.port, baudrate=self.baudrate)
                _LOGGER.info(f"Connection opened on port {self.port} with baudrate {self.baudrate}")
            except Exception as e:
                _LOGGER.error(f"Failed to open connection on port {self.port}: {e}")
                self.reader, self.writer = None, None
                raise

    async def close_connection(self):
        async with self._lock:
            if self.writer:
                try:
                    self.writer.close()
                    await self.writer.wait_closed()
                    _LOGGER.info("Connection closed successfully.")
                except Exception as e:
                    _LOGGER.error(f"Error while closing connection: {e}")
                finally:
                    self.reader, self.writer = None, None
            else:
                _LOGGER.warning("Connection was already closed or not initialized.")

    async def ensure_connection(self):
        """Ensure there is a valid connection, try to reconnect if needed."""
        if self.writer is None:
            _LOGGER.warning("No connection. Attempting to reconnect...")
            for attempt in range(3):
                try:
                    await self.open_connection()
                    return
                except Exception:
                    _LOGGER.warning(f"Reconnect attempt {attempt + 1} failed. Retrying in {self.reconnect_delay}s...")
                    await asyncio.sleep(self.reconnect_delay)
            _LOGGER.error("All reconnection attempts failed.")

    async def send_data(self, data):
        await self.ensure_connection()
        if self.writer:
            try:
                self.writer.write(data.encode())
                await self.writer.drain()
                _LOGGER.debug(f"Sent data: {data}")
            except Exception as e:
                _LOGGER.error(f"Error while sending data: {e}")
                await self.close_connection()
        else:
            _LOGGER.warning("Cannot send data: Writer is not initialized.")

    async def read_data(self):
        await self.ensure_connection()
        if self.reader:
            try:
                data = await self.reader.readuntil(b"\n")
                decoded = data.decode().strip()
                _LOGGER.debug(f"Read data: {decoded}")
                return decoded
            except Exception as e:
                _LOGGER.error(f"Error while reading data: {e}")
                await self.close_connection()
                return None
        else:
            _LOGGER.warning("Cannot read data: Reader is not initialized.")
            return None

