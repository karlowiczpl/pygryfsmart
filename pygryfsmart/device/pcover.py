from pygryfsmart import GryfApi
from pygryfsmart.const import ShutterStates
from pygryfsmart.device.classic_cover import GryfCover
from pygryfsmart.const import DriverActions, DriverFunctions

import asyncio
import logging

from .base import _GryfDevice

_LOGGER = logging.getLogger(__name__)

class GryfPCover(GryfCover):
    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 time: int,
                 api: GryfApi,
                 fun_ptr=None
                 ) -> None:

        super().__init__(
            name,
            id,
            pin,
            time,
            api,
            fun_ptr,
        )
