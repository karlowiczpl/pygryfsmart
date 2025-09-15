import asyncio
import logging
import time

from pygryfsmart import GryfApi

from pygryfsmart.const import DriverActions, OutputActions
from pygryfsmart.device.output import GryfOutput

logging.basicConfig(
        level=logging.DEBUG
        )
_LOGGER = logging.getLogger(__name__)

start_time = None
changed = 1

async def async_update(is_on):
    global start_time
    global changed

    if start_time is not None:
        elapsed = time.perf_counter() - start_time

        print(f"Responce time: {elapsed}")
        changed = 0

def start_timer():
    global start_time
    start_time = time.perf_counter()

async def async_main():
    api = GryfApi("192.168.40.95")
    output = GryfOutput(
        "test",
        95,
        1,
        api
    )

    await api.start_connection()
    output.subscribe(async_update)
    counter = 1

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
        for i in range(100):
            await api.set_pwm(1, 2, i)

            await asyncio.sleep(0.01)

if __name__ == "__main__":
    asyncio.run(async_main())
