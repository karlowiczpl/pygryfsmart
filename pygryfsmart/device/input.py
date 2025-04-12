from pygryfsmart import GryfApi
from pygryfsmart.const import CONF_IN

from .base import _GryfDevice

class GryfInput(_GryfDevice):

    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 api: GryfApi,
                 callback=None,
                 ) -> None:
        super().__init__(name,
                         id,
                         pin,
                         api)
        if callback is not None:
            self._api.subscribe(self._id , self._pin , CONF_IN , callback)

    def subscribe(self , update_fun_ptr):
        self._api.subscribe(self._id , self._pin, CONF_IN , update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}"

