from .const import (
    CONF_ID,
    CONF_PIN,
    CONF_PTR,
    CONF_FUNCTION,
    DriverFunctions,
)
from .parsing import Parser
from .typing import GryfData

import logging

_LOGGER = logging.getLogger(__name__)

class Feedback:

    _parser: Parser
    _data = GryfData()

    def __init__(self , callback=None) -> None:
        self.callback = callback
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

                    all = self._data[function]
                    current_id = all.get(sub.get(CONF_ID), {})
                    state = current_id[sub[CONF_PIN]]

                    await sub[CONF_PTR](state)
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")

    async def handle_temp_subscribtion(self , id: int , pin: int):
        pass
        for sub in self._temp_subscribers:
            if id == sub[CONF_ID] and pin == sub[CONF_PIN]:
                await sub[CONF_PTR](self._data.temps).get(id, {}).get(pin, 0)


    async def input_data(self , line):
        if line == "??????????":
            return
        try:
            parts = line.split('=')
            parsed_states = parts[1].split(',')
            last_state = parsed_states[-1].split(';')
            parsed_states[-1] = last_state[0]

            COMMAND_MAPPER = {
                DriverFunctions.INPUTS: lambda states , line : self._parser.parse_metod_1(states , line , DriverFunctions.INPUTS),
                DriverFunctions.OUTPUTS: lambda states , line : self._parser.parse_metod_1(states , line , DriverFunctions.OUTPUTS),
                DriverFunctions.PRESS_SHORT: lambda states , line : self._parser.parse_metod_2(states , line , DriverFunctions.INPUTS , 2),
                DriverFunctions.PRESS_LONG: lambda states , line : self._parser.parse_metod_2(states , line , DriverFunctions.INPUTS , 3),
                DriverFunctions.TEMP: lambda states , line : self._parser.parse_temp(states , line),
                DriverFunctions.PWM: lambda states , line : self._parser.parse_metod_3(states , line , DriverFunctions.PWM),
                DriverFunctions.COVER: lambda states , line : self._parser.parse_cover(states , line , DriverFunctions.COVER),
                DriverFunctions.FIND: lambda states , line: self._parser.parse_find(states),
                DriverFunctions.PONG: lambda states , line: self._parser.parse_pong(states),
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
