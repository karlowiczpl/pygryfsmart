import asyncio
import logging

from pygryfsmart.const import OUTPUT_STATES, SCHUTTER_STATES
from pygryfsmart.api import GryfApi
from pygryfsmart.cover import GryfCover
from pygryfsmart.gryfexpert import GryfExpert
from pygryfsmart.device import _GryfOutput , _GryfPwm , _GryfPCover , _GryfExpert

# Konfiguracja loggera
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


class controller:

    def __init__(self , device) -> None:

        self._device = device

    async def set_position(self , postion):
        self._device.set_position(self , postion)

def update(state):
    _LOGGER.debug(f"{state}")

async def main():
    # Tworzymy instancję urządzenia z odpowiednim portem i baudrate
    api = GryfApi(port="/dev/ttyUSB0")
    
    # Tworzymy instancję Controller, przekazując device
    # cont = Controller(device)
    await api.start_connection()

    # device = _GryfPCover("test" , 2 , 1 , 100 , api)
    #
    # await device.set_position(200)
    #
    # await asyncio.sleep(5)
    # _LOGGER.debug("Zmieniono pozycje na 70")
    #
    # await device.set_position(0)
    #
    # # device = _GryfOutput("test" , 1 , 3 , api , update)
    # while True:
    #     await asyncio.sleep(10)

    expert = _GryfExpert(api)

    await expert.start()

    #
    # while True:
    #     # device.available
    #     _LOGGER.debug(f"dostepnosc: {device.available}")
    #     await asyncio.sleep(5)
    #

    # cont = Controller(device)
    #
    # await asyncio.sleep(1)
    # await cont.action()
    #
    # # device.subscribe(1 , 1 , "I" , su)
    # # device.subscribe(1 , 2 , "I" , su1)
    # # device.subscribe(1 , 3 , "I" , su2)
    #
    # expert = GryfExpert(device)
    #
    # await expert.start_server()

    # cover = GryfCover(device , 2 , 1 , 100)
    # await cover.set_cover_position(100)
    #
    # await asyncio.sleep(3)
    #
    # await cover.set_cover_position(50)
    
    

if __name__ == "__main__":
    asyncio.run(main())
