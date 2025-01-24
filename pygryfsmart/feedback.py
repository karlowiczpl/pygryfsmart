import logging 

from pygryfsmart.const import (
    DATA_FEEDBACK_PONG,
    DATA_IN,
    DATA_OUT,
    DATA_TEMP,
    DATA_ROL,
    DATA_PWM,

    DATA_FEEDBACK_IN,
    DATA_FEEDBACK_OUT,
    DATA_FEEDBACK_TEMP,
    DATA_FEEDBACK_ROL,
    DATA_FEEDBACK_PWM,
    DATA_FEEDBACK_PRESS_SHORT,
    DATA_FEEDBACK_PRESS_LONG,
    DATA_FEEDBACK_PONG
)

_LOGGER = logging.getLogger(__name__)

class Feedback:
    def __init__(self , callback=None) -> None:
        self.callback = callback
        self._data = {
            DATA_IN: {},
            DATA_OUT: {},
            DATA_TEMP: {},
            DATA_ROL: {},
            DATA_PWM: {},
        }
    
    @property
    def data(self):
        return self._data

    async def input_data(self , line):
        if line == "??????????":
            return
        try:
            parts = line.split('=')
            parsed_states = parts[1].split(',')
            last_state = parsed_states[-1].split(';')
            parsed_states[-1] = last_state[0]

            if parts[0] == DATA_FEEDBACK_IN:
                if len(parsed_states) not in {7 , 9}:
                    raise ValueError(f"Invalid number of arguments: {line}")

                for i in range(1, len(parsed_states)):
                    if parsed_states[i] not in {"0" , "1"}:
                        raise ValueError(f"Wrong parameter value: {line}")

                    pin = int(parsed_states[0])
                    if pin not in self._data[DATA_IN]:
                        self._data[DATA_IN][pin] = {}
                    self._data[DATA_IN][pin][i] = int(parsed_states[i])                   

            if parts[0] == DATA_FEEDBACK_OUT:
                if len(parsed_states) not in {7 , 9}:
                    raise ValueError(f"Invalid number of arguments: {line}")

                for i in range(1, len(parsed_states)):
                    if parsed_states[i] not in {"0" , "1"}: 
                        raise ValueError(f"Wrong parameter value: {line}")

                    pin = int(parsed_states[0])
                    if pin not in self._data[DATA_OUT]:
                        self._data[DATA_OUT][pin] = {}
                    self._data[DATA_OUT][pin][i] = int(parsed_states[i])                   

            if parts[0] == DATA_FEEDBACK_PRESS_SHORT:
                if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
                    raise ValueError(f"Argument out of scope: {line}")

                pin = int(parsed_states[1])
                id = int(parsed_states[0])
                if id not in self._data[DATA_IN]:
                    self._data[DATA_IN][id] = {}
                self._data[DATA_IN][id][pin] = 2

            if parts[0] == DATA_FEEDBACK_PRESS_LONG:
                if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
                    raise ValueError(f"Argument out of scope: {line}")

                pin = int(parsed_states[1])
                id = int(parsed_states[0])
                if id not in self._data[DATA_IN]:
                    self._data[DATA_IN][id] = {}
                self._data[DATA_IN][id][pin] = 3

            if parts[0] == DATA_FEEDBACK_TEMP:
                if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
                    raise ValueError(f"Argument out of scope: {line}")

                pin = int(parsed_states[1])
                id = int(parsed_states[0])
                if id not in self._data[DATA_TEMP]:
                    self._data[DATA_TEMP][id] = {}
                self._data[DATA_TEMP][id][pin] = float(f"{parsed_states[2]}.{parsed_states[3]}")

            if parts[0] == DATA_FEEDBACK_PONG:
                self._last_ping = int(parsed_states[0])

            _LOGGER.debug(f"Parsed data: {self._data}")

            if self.callback:
                await self.callback(self._data) 
        except Exception as e:
            _LOGGER.error(f"ERROR parsing data: {e}")
