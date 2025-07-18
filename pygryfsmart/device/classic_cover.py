from pygryfsmart import GryfApi
from pygryfsmart.const import ShutterStates, DriverFunctions

from .base import _GryfDevice

class GryfCover(_GryfDevice):

    def __init__(
        self,
        name: str,
        id: int,
        pin: int,
        time: int,
        api: GryfApi,
    ):
        super().__init__(name,
                         id,
                         pin,
                         api)

        self._time = time

        self._attributes = {
            "id": id,
            "pin": pin,
            "time": time
        }

    def subscribe(self , update_fun_ptr):
        self._api.subscribe(self._id , self._pin, DriverFunctions.COVER , update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}"

    async def turn_on(self):
        await self._api.set_cover(self._id , self._pin , self._time , ShutterStates.OPEN)

    async def turn_off(self):
        await self._api.set_cover(self._id , self._pin , self._time , ShutterStates.CLOSE)

    async def toggle(self):
        await self._api.set_cover(self._id , self._pin , self._time , ShutterStates.STEP_MODE)

    async def stop(self):
        await self._api.set_cover(self._id , self._pin , self._time , ShutterStates.STOP)
