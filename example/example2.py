import asyncio
import logging
import time

from pygryfsmart import GryfApi

from pygryfsmart.const import DriverActions, OutputActions
from pygryfsmart.device.classic_cover import GryfCover
from pygryfsmart.device.pcover import GryfPCover
from pygryfsmart.device.output import GryfOutput

logging.basicConfig(
        level=logging.DEBUG
        )
_LOGGER = logging.getLogger(__name__)

async def async_update(state):
    # _LOGGER.debug(state)
    pass

async def async_main():

    api = GryfApi("/dev/ttyACM0")

    cover = GryfPCover("test", 2, 1, 50, api)
    cover.subscribe(async_update)

    await api.start_connection()
    api.start_update_interval(1)

    await cover.turn_on()

    while 1:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(async_main())
