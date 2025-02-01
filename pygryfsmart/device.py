from datetime import datetime
import logging

from example.example import update
from pygryfsmart.api import GryfApi
from pygryfsmart.const import (
    COMMAND_FUNCTION_PONG,
    COMMAND_FUNCTION_TEMP,
    OUTPUT_STATES,
    COMMAND_FUNCTION_IN,
    COMMAND_FUNCTION_OUT,
)

_LOGGER = logging.getLogger(__name__)

class _GryfDevice:
    _name: str
    _id: int
    _pin: int
    _api: GryfApi

    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 api: GryfApi
                 ) -> None:
        self._name = name
        self._id = id
        self._pin = pin
        self._api = api

        now = datetime.now()
        self._api.feedback.data[COMMAND_FUNCTION_PONG][self._id] = now.strftime("%H:%M") 

    @property
    def available(self):
        return self._api.avaiable_module(self._id)

class _GryfOutput(_GryfDevice):
    def __init__(
        self,
        name: str,
        id: int,
        pin: int,
        api: GryfApi,
        fun_ptr
    ):
        super().__init__(name,
                         id,
                         pin,
                         api)
        self._api.subscribe(self._id, self._pin, COMMAND_FUNCTION_OUT, fun_ptr)

    @property
    def name(self):
        return f"{self._name}_GRYF"

    async def turn_on(self):
        await self._api.set_out(self._id, self._pin, OUTPUT_STATES.ON)

    async def turn_off(self):
        await self._api.set_out(self._id, self._pin, OUTPUT_STATES.OFF)

    async def toggle(self):
        await self._api.set_out(self._id, self._pin, OUTPUT_STATES.TOGGLE)

class _GryfInput(_GryfDevice):

    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 api: GryfApi,
                 update_fun_ptr,
                 ) -> None:
        super().__init__(name,
                         id,
                         pin,
                         api)

        self._api.subscribe(id , pin , COMMAND_FUNCTION_IN , update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}_GRYF"

class _GryfTemperature(_GryfDevice):
    
    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 api: GryfApi,
                 update_fun_ptr) -> None:
        super().__init__(name, 
                         id, 
                         pin, 
                         api)

        self._api.subscribe(id , pin , COMMAND_FUNCTION_TEMP , update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}_GRYF"
