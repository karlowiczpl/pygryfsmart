import asyncio
import logging
import time

from pygryfsmart import GryfApi

from pygryfsmart.const import DriverActions, OutputActions
from pygryfsmart.device.classic_cover import GryfCover
from pygryfsmart.device.output import GryfOutput

logging.basicConfig(
        level=logging.DEBUG
        )
_LOGGER = logging.getLogger(__name__)


async def async_update(is_on):
    _LOGGER.debug("is_on: " + str(is_on))

def start_timer():
    global start_time
    start_time = time.perf_counter()

async def async_main():
    # api = GryfApi("192.168.40.95")
    api = GryfApi("/dev/ttyACM0")
    output = GryfOutput(
        "test",
        95,
        1,
        api
    )
    output.subscribe(async_update)

    cover = GryfCover("test", 2, 1, 5, api)


    await api.start_connection()
    api.start_update_interval(1)
    cover.subscribe(async_update)

    await cover.turn_on()

    while 1:
        # global changed
        # changed = 1
        # start_timer()
        # 
        # if counter:
        #     await output.turn_on()
        #     counter = 0
        # else:
        #     await output.turn_off()
        #     counter = 1
        #
        # while changed:
        #     await asyncio.sleep(0.1)
        #
        # await asyncio.sleep(1)
        # for i in range(100):
        #     await api.set_pwm(1, 2, i)

            await asyncio.sleep(0.001)

if __name__ == "__main__":
    asyncio.run(async_main())
