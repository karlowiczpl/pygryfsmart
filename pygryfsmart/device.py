from pygryfsmart.rs232 import RS232Handler
from pygryfsmart.const import BAUDRATE

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class Device(RS232Handler):
    def __init__(self, port , callback = None):
        super().__init__(port, BAUDRATE)
        self.data = {
            "IN": {},
            "OUT": {},
            "TEMP": {},
            "ROL": {},
            "PWM": {},
        }
        self._update_task = None
        self._connection_task = None
        self._last_ping = 0
        self.callback = callback

    async def stop_connection(self):
        if self._connection_task:
            self._connection_task.cancel()
            try:
                await self._connection_task
            except asyncio.CancelledError:
                _LOGGER.debug("Connection task was cancelled.")
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                _LOGGER.debug("Update task was cancelled.")
        await self.close_connection()
        _LOGGER.debug("Connection closed.")

    async def connection_task(self):
        try:
            while True:
                line = await super().read_data()
                _LOGGER.debug(f"Received data: {line}")
                await self.__parse_data(line)
        except asyncio.CancelledError:
            _LOGGER.info("Connection task cancelled.")
            await self.close_connection()
            raise
        except Exception as e:
            _LOGGER.error(f"Error in connection task: {e}")
            await self.close_connection()
            raise

    async def send_command(self, data):
        return await super().send_data(data)
    
    async def start_connection(self):
        await super().open_connection()
        self._connection_task = asyncio.create_task(self.connection_task())
        _LOGGER.info("Connection task started.")

    async def send_data(self, data):
        await super().send_data(data)

    async def set_out(self, id: int, pin: int , state):
        states = ["0"] * 8 if pin > 6 else ["0"] * 6
        states[pin - 1] = str(state)

        command = f"AT+SetOut={id}," + ",".join(states) + "\n\r"
        await self.send_data(command)

    async def set_key_time(self , ps_time: int , pl_time: int , id: int , pin: int , type):
        command = f"AT+Key={id},{pin},{ps_time},{pl_time},{type}\n\r"
        await self.send_data(command)

    async def search_module(self , id):
        command = f"AT+Search=0,{id}\n\r"
        await self.send_data(command)

    async def ping(self , module_id: int):
        command = f"PING={module_id}\n\r"
        await self.send_data(command)
        await asyncio.sleep(0.1)
        if self._last_ping == module_id:
            self._last_ping = 0
            return True
        self._last_ping = 0
        return False
    
    async def set_led(self , id: int , pin: int , level: int):
        command = f"SetLED={id},{pin},{level}\n\r"
        await self.send_data(command)

    async def set_rol(self , id: int , pin: int , time: int , operation):
        if operation in {1 , 2 , 3 , 4} and pin in {1 , 2 , 3 , 4}:
            states = ["0"] * 4
            states[pin - 1] = str(operation)
            control_sum = id + time + int(states[0]) + int(states[1]) + int(states[2]) + int(states[3])

            command = f"AT+SetRol={id},{time},{states[0]},{states[1]},{states[2]},{states[3]},{control_sum}\n\r"
            await self.send_data(command)
        else:
            raise ValueError(f"Argument out of scope: id: {id} , pin: {pin} , time: {time}, operation: {operation}")

    async def reset(self , module_id: int , update_states: bool):
        if module_id == 0:
            command = "AT+RST=0\n\r"
            await self.send_data(command)
            if update_states == True:
                module_count = len(self.data["OUT"])
                await asyncio.sleep(2)
                for i in range(module_count):
                    states = ",".join(map(str, self.data["OUT"][i]))
                    command = f"AT+SetOut={i},{states}\n\r"
                    await self.send_data(command)
    
    async def __parse_data(self , line):
        if line == "??????????":
            return
        try:
            parts = line.split('=')
            parsed_states = parts[1].split(',')
            last_state = parsed_states[-1].split(';')
            parsed_states[-1] = last_state[0]

            if parts[0] == "I":
                if len(parsed_states) not in {7 , 9}:
                    raise ValueError(f"Invalid number of arguments: {line}")

                for i in range(1, len(parsed_states)):
                    if parsed_states[i] not in {"0" , "1"}:
                        raise ValueError(f"Wrong parameter value: {line}")

                    pin = int(parsed_states[0])
                    if pin not in self.data["IN"]:
                        self.data["IN"][pin] = {}
                    self.data["IN"][pin][i] = int(parsed_states[i])                   

            if parts[0] == "O":
                if len(parsed_states) not in {7 , 9}:
                    raise ValueError(f"Invalid number of arguments: {line}")

                for i in range(1, len(parsed_states)):
                    if parsed_states[i] not in {"0" , "1"}: 
                        raise ValueError(f"Wrong parameter value: {line}")

                    pin = int(parsed_states[0])
                    if pin not in self.data["OUT"]:
                        self.data["OUT"][pin] = {}
                    self.data["OUT"][pin][i] = int(parsed_states[i])                   

            if parts[0] == "PS":
                if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
                    raise ValueError(f"Argument out of scope: {line}")

                pin = int(parsed_states[1])
                id = int(parsed_states[0])
                if id not in self.data["IN"]:
                    self.data["IN"][id] = {}
                self.data["IN"][id][pin] = 2

            if parts[0] == "PL":
                if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
                    raise ValueError(f"Argument out of scope: {line}")

                pin = int(parsed_states[1])
                id = int(parsed_states[0])
                if id not in self.data["IN"]:
                    self.data["IN"][id] = {}
                self.data["IN"][id][pin] = 3

            if parts[0] == "T":
                if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
                    raise ValueError(f"Argument out of scope: {line}")

                pin = int(parsed_states[1])
                id = int(parsed_states[0])
                if id not in self.data["TEMP"]:
                    self.data["TEMP"][id] = {}
                self.data["TEMP"][id][pin] = float(f"{parsed_states[2]}.{parsed_states[3]}")

            if parts[0] == "PONG":
                self._last_ping = int(parsed_states[0])

            _LOGGER.debug(f"Parsed data: {self.data}")

            if self.callback:
                await self.callback(line) 
        except Exception as e:
            _LOGGER.error(f"ERROR parsing data: {e}")

    def start_update_interval(self, time):
        if not self._update_task:
            self._update_task = asyncio.create_task(self.__states_update_interval(time))
            _LOGGER.info("Update interval task started.")

    async def __states_update_interval(self, time):
        try:
            while True:
                module_count = max(len(self.data["IN"]), len(self.data["OUT"]))

                for i in range(module_count):
                    try:
                        command = f"AT+StanIN={i + 1}\n\r"
                        await self.send_data(command)
                        await asyncio.sleep(0.1)

                        command = f"AT+StanOUT={i + 1}\n\r"
                        await self.send_data(command)
                    except Exception as e:
                        _LOGGER.error(f"Error updating module {i + 1}: {e}")

                await asyncio.sleep(time)
        except asyncio.CancelledError:
            _LOGGER.info("Update interval task cancelled.")
        except Exception as e:
            _LOGGER.error(f"Error in update interval: {e}")
