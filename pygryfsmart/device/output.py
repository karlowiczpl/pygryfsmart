from pygryfsmart.const import CONF_OUT , OUTPUT_STATES
from pygryfsmart import GryfApi

from .base import _GryfDevice

class GryfOutput(_GryfDevice):
    def __init__(
        self,
        name: str,
        id: int,
        pin: int,
        api: GryfApi,
        update_fun_ptr=None,
    ):
        super().__init__(name,
                         id,
                         pin,
                         api)
        if update_fun_ptr:
            self._api.subscribe(self._id , self._pin , CONF_OUT , update_fun_ptr)

    def subscribe(self , update_fun_ptr):
        self._api.subscribe(self._id , self._pin, CONF_OUT , update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}"

    async def turn_on(self):
        await self._api.set_out(self._id, self._pin, OUTPUT_STATES.ON)

    async def turn_off(self):
        await self._api.set_out(self._id, self._pin, OUTPUT_STATES.OFF)

    async def toggle(self):
        await self._api.set_out(self._id, self._pin, OUTPUT_STATES.TOGGLE)
