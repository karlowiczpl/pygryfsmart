from .const import (
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
from .parsing import Parser

import logging


_LOGGER = logging.getLogger(__name__)

class Feedback:

    _parser: Parser

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
        self._parser = Parser(self)

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
        pass
        for sub in self._temp_subscribers:
            if id == sub[CONF_ID] and pin == sub[CONF_PIN]:
                await sub[CONF_PTR](self._data.get(COMMAND_FUNCTION_TEMP , {}).get(id , {}).get(pin , 0))


    async def input_data(self , line):
        if line == "??????????":
            return
        try:
            parts = line.split('=')
            parsed_states = parts[1].split(',')
            last_state = parsed_states[-1].split(';')
            parsed_states[-1] = last_state[0]

            COMMAND_MAPPER = {
                COMMAND_FUNCTION_IN: lambda states , line : self._parser.parse_metod_1(states , line , COMMAND_FUNCTION_IN),
                COMMAND_FUNCTION_OUT: lambda states , line : self._parser.parse_metod_1(states , line , COMMAND_FUNCTION_OUT),
                COMMAND_FUNCTION_PRESS_SHORT: lambda states , line : self._parser.parse_metod_2(states , line , COMMAND_FUNCTION_IN , 2),
                COMMAND_FUNCTION_PRESS_LONG: lambda states , line : self._parser.parse_metod_2(states , line , COMMAND_FUNCTION_IN , 3),
                COMMAND_FUNCTION_TEMP: lambda states , line : self._parser.parse_temp(states , line),
                COMMAND_FUNCTION_PWM: lambda states , line : self._parser.parse_metod_3(states , line , COMMAND_FUNCTION_PWM),
                COMMAND_FUNCTION_COVER: lambda states , line : self._parser.parse_cover(states , line , COMMAND_FUNCTION_COVER),
                COMMAND_FUNCTION_FIND: lambda states , line: self._parser.parse_find(states),
                COMMAND_FUNCTION_PONG: lambda states , line: self._parser.parse_pong(states),
            }

            if str(parts[0]).upper() in COMMAND_MAPPER:
                await COMMAND_MAPPER[str(parts[0]).upper()](parsed_states , line)

            if self.callback:
                await self.callback() 

        except Exception as e:
            _LOGGER.error(f"ERROR parsing data: {e}")

    def subscribe(self , conf: dict):
        self._subscribers.append(conf)

    def subscribe_temp(self , conf: dict):
        self._temp_subscribers.append(conf)
