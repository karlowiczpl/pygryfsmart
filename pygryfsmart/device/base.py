from pygryfsmart.const import CONF_PONG
from pygryfsmart import GryfApi

from datetime import datetime

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
        self._api.feedback.data[CONF_PONG][self._id] = now.strftime("%H:%M") 

    @property
    def available(self):
        return self._api.avaiable_module(self._id)
