from pygryfsmart.feedback import Feedback
from pygryfsmart.rs232 import RS232Handler
from pygryfsmart.gryfexpert import GryfExpert
from pygryfsmart.const import (
    BAUDRATE,
    COMMAND_FUNCTION_COVER,
    COMMAND_FUNCTION_PONG,
    COMMAND_FUNCTION_PWM,
    COMMAND_FUNCTION_TEMP,
    KEY_MODE,
    OUTPUT_STATES,
    SCHUTTER_STATES,

    COMMAND_FUNCTION_IN,
    COMMAND_FUNCTION_OUT,

    COMMAND_FUNCTION_GET_IN_STATE,
    COMMAND_FUNCTION_GET_OUT_STATE,
    COMMAND_FUNCTION_SET_OUT,
    COMMAND_FUNCTION_SET_COVER,
    COMMAND_FUNCTION_SET_PWM,
    COMMAND_FUNCTION_PING,
    COMMAND_FUNCTION_SET_PRESS_TIME,
    COMMADN_FUNCTION_SEARCH_MODULE,

    CONF_ID,
    CONF_PIN,
    CONF_PTR,
    CONF_FUNCTION
)

import asyncio
import logging
from datetime import datetime , timedelta

_LOGGER = logging.getLogger(__name__)

class GryfApi(RS232Handler):
    _gryf_expert: GryfExpert

    def __init__(self, port , callback = None):
        super().__init__(port, BAUDRATE)
        self.feedback = Feedback(callback=callback)

        self._update_task = None
        self._connection_task = None
        self._last_ping = 0
        self._input_message_subscribers = []
        self._output_message_subscribers = []

    async def sending_data_to_gryf_expert(self , message):
        if self._gryf_expert.enable == True:
            await self._gryf_expert.send_data(message)

    def subscribe_input_message(self, func):
        self._input_message_subscribers.append(func)

    def subscribe_output_message(self , func):
        self._output_message_subscribers.append(func)

    def avaiable_module(self , id: int) -> bool:
        last_call = self.feedback.data[COMMAND_FUNCTION_PONG].get(1 , None)
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        if last_call == None:
            return False

        now_dt = datetime.strptime(current_time , "%H:%M")
        last_dt = datetime.strptime(last_call , "%H:%M")

        if now_dt - last_dt < timedelta(minutes=2):
            return True
        return False

    def ping_connection(self):
        return self.ping(1)

    def subscribe(self , id , pin , func, ptr):
        if func in {COMMAND_FUNCTION_IN,
                    COMMAND_FUNCTION_OUT,
                    COMMAND_FUNCTION_TEMP,
                    COMMAND_FUNCTION_PWM,
                    COMMAND_FUNCTION_COVER}:
            data = {
                CONF_ID: id,
                CONF_PIN: pin,
                CONF_FUNCTION: func,
                CONF_PTR: ptr
            }
            if func != COMMAND_FUNCTION_TEMP:
                self.feedback.subscribe(data)
            else:
                self.feedback.subscribe_temp(data)
        else:
            _LOGGER.error(f"Bad function to subscribe: {func}")

    def set_callback(self , callback):
        self.feedback.callback = callback

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

    async def __connection_task(self):
        try:
            while True:
                line = await super().read_data()
                _LOGGER.debug(f"Received data: {line}")
                await self.feedback.input_data(line)
                if self._input_message_subscribers:
                    for subscribers in self._input_message_subscribers:
                        await subscribers(line)
        except asyncio.CancelledError:
            _LOGGER.info("Connection task cancelled.")
            await self.close_connection()
            raise
        except Exception as e:
            _LOGGER.error(f"Error in connection task: {e}")
            await self.close_connection()
            raise

    async def start_connection(self):
        await super().open_connection()
        self._connection_task = asyncio.create_task(self.__connection_task())
        _LOGGER.info("Connection task started.")

    async def send_data(self, data):
        await super().send_data(data)

        for subscribers in self._output_message_subscribers:
            subscribers(data)

    async def set_out(self, id: int, pin: int , state: OUTPUT_STATES | int):
        states = ["0"] * 8 if pin > 6 else ["0"] * 6
        states[pin - 1] = str(state)

        command = f"{COMMAND_FUNCTION_SET_OUT}={id}," + ",".join(states) + "\n\r"
        await self.send_data(command)

    async def set_key_time(self , ps_time: int , pl_time: int , id: int , pin: int , type: KEY_MODE | int):
        command = f"{COMMAND_FUNCTION_SET_PRESS_TIME}={id},{pin},{ps_time},{pl_time},{type}\n\r"
        await self.send_data(command)

    async def search_module(self , id: int):
        if id != 0:
            command = f"{COMMADN_FUNCTION_SEARCH_MODULE}=0,{id}\n\r"
            await self.send_data(command)

    async def search_modules(self , last_module: int):
        for i in range(last_module):
            command = f"{COMMADN_FUNCTION_SEARCH_MODULE}=0,{i + 1}\n\r"
            await self.send_data(command)

    async def ping(self , module_id: int):
        command = f"{COMMAND_FUNCTION_PING}={module_id}\n\r"
        await self.send_data(command)
        await asyncio.sleep(0.05)
        if self._last_ping == module_id:
            self._last_ping = 0
            return True
        self._last_ping = 0
        return False
    
    async def set_pwm(self , id: int , pin: int , level: int):
        command = f"{COMMAND_FUNCTION_SET_PWM}={id},{pin},{level}\n\r"
        await self.send_data(command)

    async def set_cover(self , id: int , pin: int , time: int , operation: SCHUTTER_STATES | int):
        if operation in {SCHUTTER_STATES.CLOSE , SCHUTTER_STATES.OPEN , SCHUTTER_STATES.STOP , SCHUTTER_STATES.STEP_MODE} and pin in {1 , 2 , 3 , 4}:
            states = ["0"] * 4
            states[pin - 1] = str(operation)
            control_sum = id + time + int(states[0]) + int(states[1]) + int(states[2]) + int(states[3])

            command = f"{COMMAND_FUNCTION_SET_COVER}={id},{time},{states[0]},{states[1]},{states[2]},{states[3]},{control_sum}\n\r"
            await self.send_data(command)
        else:
            raise ValueError(f"Argument out of scope: id: {id} , pin: {pin} , time: {time}, operation: {operation}")

    async def reset(self , module_id: int , update_states: bool):
        if module_id == 0:
            command = "AT+RST=0\n\r"
            await self.send_data(command)
            if update_states == True:
                module_count = len(self.feedback.data[COMMAND_FUNCTION_OUT])
                await asyncio.sleep(2)
                states = self.feedback.data[COMMAND_FUNCTION_OUT]
                for i in range(module_count):
                    tabble = list(self.feedback.data[COMMAND_FUNCTION_OUT][i+1].values())
                    states = ",".join(map(str, tabble))
                    command = f"AT+SetOut={i+1},{states}\n\r"
                    await self.send_data(command)

    def start_update_interval(self, time: int):
        if not self._update_task:
            self._update_task = asyncio.create_task(self.__states_update_interval(time))
            _LOGGER.info("Update interval task started.")

    async def __states_update_interval(self, time: int):
        try:
            while True:
                module_count = max(len(self.feedback.data[COMMAND_FUNCTION_IN]), len(self.feedback.data[COMMAND_FUNCTION_OUT]))

                for i in range(module_count):
                    try:
                        command = f"{COMMAND_FUNCTION_GET_IN_STATE}={i + 1}\n\r"
                        await self.send_data(command)
                        await asyncio.sleep(0.1)

                        command = f"{COMMAND_FUNCTION_GET_OUT_STATE}={i + 1}\n\r"
                        await self.send_data(command)
                    except Exception as e:
                        _LOGGER.error(f"Error updating module {i + 1}: {e}")

                await asyncio.sleep(time)
        except asyncio.CancelledError:
            _LOGGER.info("Update interval task cancelled.")
        except Exception as e:
            _LOGGER.error(f"Error in update interval: {e}")
