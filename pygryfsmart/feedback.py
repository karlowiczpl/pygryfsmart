from pygryfsmart.const import (
    COMMAND_FUNCTION_IN,
    COMMAND_FUNCTION_OUT,
    COMMAND_FUNCTION_PWM,
    COMMAND_FUNCTION_COVER,
    COMMAND_FUNCTION_FIND,
    COMMAND_FUNCTION_PONG,
    COMMAND_FUNCTION_PRESS_SHORT,
    COMMAND_FUNCTION_PRESS_LONG,
    COMMAND_FUNCTION_TEMP,

    CONF_ID,
    CONF_PIN,
    CONF_PTR,
    CONF_FUNCTION,
)

from datetime import datetime
import logging

_LOGGER = logging.getLogger(__name__)

class Feedback:
    def __init__(self , callback=None) -> None:
        self.callback = callback
        self._data = {
            COMMAND_FUNCTION_IN: {},
            COMMAND_FUNCTION_OUT: {},
            COMMAND_FUNCTION_PWM: {},
            COMMAND_FUNCTION_COVER: {},
            COMMAND_FUNCTION_FIND: {},
            COMMAND_FUNCTION_PONG: {},
            COMMAND_FUNCTION_TEMP: {},
        }
        self._subscribers = []
        self._temp_subscribers = []

    @property
    def data(self):
        return self._data

    async def handle_subscribtion(self , function: str):
        try:
            for sub in self._subscribers:
                if function == sub[CONF_FUNCTION]:
                    await sub[CONF_PTR](self._data.get(function , {}).get(sub.get(CONF_ID) , {}).get(sub.get(CONF_PIN) , 0))
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")

    async def handle_temp_subscribtion(self , id: int , pin: int):
        for sub in self._temp_subscribers:
            if id == sub[CONF_ID] and pin == sub[CONF_PIN]:
                await sub[CONF_PIN](self._data.get(COMMAND_FUNCTION_TEMP , {}).get(id , {}).get(pin , 0))

    async def __parse_metod_1(self , parsed_states , line: str , function: str):
        if len(parsed_states) not in {7 , 9}:
            raise ValueError(f"Invalid number of arguments: {line}")

        for i in range(1, len(parsed_states)):
            if parsed_states[i] not in {"0" , "1"}:
                raise ValueError(f"Wrong parameter value: {line}")

            pin = int(parsed_states[0])
            if pin not in self._data[function]:
                self._data[function][pin] = {}
            self._data[function][pin][i] = int(parsed_states[i])                   
        try:
            await self.handle_subscribtion(function)
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")

        now = datetime.now()
        self._data[COMMAND_FUNCTION_PONG][int(parsed_states[0])] = now.strftime("%H:%M")

    async def __parse_metod_2(self , parsed_states , line: str , function: str , prefix: int):
        if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
            raise ValueError(f"Argument out of scope: {line}")

        pin = int(parsed_states[1])
        id = int(parsed_states[0])
        if id not in self._data[function]:
            self._data[function][id] = {}
        self._data[function][id][pin] = prefix
        try:
            await self.handle_subscribtion(function)
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")

    async def __parse_metod_3(self , parsed_states , line: str , function: str):
        if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
            raise ValueError(f"Argument out of scope: {line}")

        pin = int(parsed_states[1])
        id = int(parsed_states[0])
        if id not in self._data[function]:
            self._data[function][id] = {}
        self._data[function][id][pin] = parsed_states[2]
        try:
            await self.handle_subscribtion(function)
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")

    async def __parse_cover(self , parsed_states , line: str , function: str):
        if len(parsed_states) != 5:
            raise ValueError(f"Invalid number of arguments: {line}")

        for i in range(1, len(parsed_states)):
            if parsed_states[i] not in {"0" , "1"}:
                raise ValueError(f"Wrong parameter value: {line}")

            pin = int(parsed_states[0])
            if pin not in self._data[function]:
                self._data[function][pin] = {}
            self._data[function][pin][i] = int(parsed_states[i])                   
        try:
            await self.handle_subscribtion(function)
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")

    async def __parse_temp(self , parsed_states , line: str):
        if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
            raise ValueError(f"Argument out of scope: {line}")

        pin = int(parsed_states[1])
        id = int(parsed_states[0])
        if id not in self._data[COMMAND_FUNCTION_TEMP]:
            self._data[COMMAND_FUNCTION_TEMP][id] = {}
        self._data[COMMAND_FUNCTION_TEMP][id][pin] = float(f"{parsed_states[2]}.{parsed_states[3]}")
        try:
            await self.handle_temp_subscribtion(id , pin)
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")

    async def __parse_find(self , parsed_states):
        id = int(parsed_states[0])
        self._data[COMMAND_FUNCTION_FIND][id] = float(f"{parsed_states[1]}.{parsed_states[2]}")

    async def __parse_pong(self , parsed_states):
        now = datetime.now()

        id = int(parsed_states[0])
        self._data[COMMAND_FUNCTION_PONG][id] = now.strftime("%H:%M")
    
    def subscribe(self , conf: dict):
        self._subscribers.append(conf)

    def subscribe_temp(self , conf: dict):
        self._temp_subscribers.append(conf)

    async def input_data(self , line):
        if line == "??????????":
            return
        try:
            parts = line.split('=')
            parsed_states = parts[1].split(',')
            last_state = parsed_states[-1].split(';')
            parsed_states[-1] = last_state[0]
            _LOGGER.debug(f"{parsed_states}")

            COMMAND_MAPPER = {
                COMMAND_FUNCTION_IN: lambda states , line : self.__parse_metod_1(states , line , COMMAND_FUNCTION_IN),
                COMMAND_FUNCTION_OUT: lambda states , line : self.__parse_metod_1(states , line , COMMAND_FUNCTION_OUT),
                COMMAND_FUNCTION_PRESS_SHORT: lambda states , line : self.__parse_metod_2(states , line , COMMAND_FUNCTION_IN , 2),
                COMMAND_FUNCTION_PRESS_LONG: lambda states , line : self.__parse_metod_2(states , line , COMMAND_FUNCTION_IN , 3),
                COMMAND_FUNCTION_TEMP: lambda states , line : self.__parse_temp(states , line),
                COMMAND_FUNCTION_PWM: lambda states , line : self.__parse_metod_3(states , line , COMMAND_FUNCTION_PWM),
                COMMAND_FUNCTION_COVER: lambda states , line : self.__parse_cover(states , line , COMMAND_FUNCTION_COVER),
                COMMAND_FUNCTION_FIND: lambda states , line: self.__parse_find(states),
                COMMAND_FUNCTION_PONG: lambda states , line: self.__parse_pong(states),
            }

            if str(parts[0]).upper() in COMMAND_MAPPER:
                await COMMAND_MAPPER[str(parts[0]).upper()](parsed_states , line)

            if self.callback:
                await self.callback() 

        except Exception as e:
            _LOGGER.error(f"ERROR parsing data: {e}")
