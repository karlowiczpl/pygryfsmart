import asyncio
import logging

from pygryfsmart.const import OUTPUT_STATES, SCHUTTER_STATES
from pygryfsmart.api import GryfApi
from pygryfsmart.cover import GryfCover
from pygryfsmart.gryfexpert import GryfExpert
from pygryfsmart.device import _GryfOutput , _GryfPwm

# Konfiguracja loggera
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

class Controller:
    def __init__(self, device: GryfApi):
        self.device = device
        device.set_callback(self.on_data_received)

    @property
    def data(self):
        return self.device.feedback.data

    async def on_data_received(self):
        _LOGGER.debug("%s" , self.data)
        # Tutaj możesz dodać dowolną logikę, która ma być aktywowana na przychodzące dane
        # np. analiza danych, zmiana stanu, wywołanie innych funkcji, itd.

    async def start(self):
        await self.device.start_connection()
        _LOGGER.info("Device connection started.")

    async def action(self):
        pass

async def su(state):
    _LOGGER.debug("state: %s" , state)
async def su1(state):
    _LOGGER.debug("state1: %s" , state)
async def su2(state):
    _LOGGER.debug("state2: %s" , state)

def update(state):
    _LOGGER.debug(f"{state}")

async def main():
    # Tworzymy instancję urządzenia z odpowiednim portem i baudrate
    api = GryfApi(port="/dev/ttyUSB0")
    
    # Tworzymy instancję Controller, przekazując device
    # cont = Controller(device)
    await api.start_connection()

    device = _GryfPwm("test" , 1 , 1 , api)
    device.subscribe(update)

    await device.set_level(54)
    await asyncio.sleep(3)
    await device.turn_off()
    await asyncio.sleep(3)
    await device.toggle()
    await asyncio.sleep(3)
    await device.turn_off()
    await asyncio.sleep(3)
    await device.turn_on()
    # device = _GryfOutput("test" , 1 , 3 , api , update)
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
    
    
    # Rozpoczynamy połączenie
    while True:
        await asyncio.sleep(5)
        await expert.send_data("test\n")

if __name__ == "__main__":
    asyncio.run(main())
