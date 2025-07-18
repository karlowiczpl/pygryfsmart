import asyncio
import logging

from pygryfsmart import GryfApi

from pygryfsmart.const import OutputActions

logging.basicConfig(
        level=logging.DEBUG
        )
_LOGGER = logging.getLogger(__name__)

async def async_main():
    api = GryfApi("31.186.217.232")

    await api.start_connection()

    await api.set_out(1, 1, OutputActions.ON)

    await api.search_module(1)

    while 1:
        await asyncio.sleep(4)

        _LOGGER.debug(api.feedback.data)

        await api.reset(0, True)

if __name__ == "__main__":
    asyncio.run(async_main())
