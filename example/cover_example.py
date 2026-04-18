import asyncio
import logging

from pygryfsmart import GryfApi
from pygryfsmart.const import OutputActions, OutputStates
from pygryfsmart.device import GryfOutput, GryfCover
from pygryfsmart.device.output_line import GryfOutputLine

from pygryfsmart.device import GryfPercentCover


logging.basicConfig(
        level=logging.DEBUG
        )
_LOGGER = logging.getLogger(__name__)

def async_update(self, state):
    _LOGGER.debug(f"Actual cover state: {state}")

async def main():
    api = GryfApi("/dev/ttyACM0")
    await api.start_connection()

    cover_device = GryfPercentCover(
        "Test Shutter",
        2,
        1,
        100,
        api
    )

    api.set_cover_toggle_metod(0)
    await asyncio.sleep(1)

    await cover_device.set_cover_position(100)

    await asyncio.sleep(2)

    await cover_device.set_cover_position(50)

    await asyncio.sleep(3)

    await cover_device.set_cover_position(0)

    await asyncio.sleep(1)

    await cover_device.set_cover_position(100)

    while True:

        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
