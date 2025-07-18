import asyncio
import logging

from pygryfsmart import GryfApi
from pygryfsmart.const import OutputActions, OutputStates
from pygryfsmart.device import GryfOutput
from pygryfsmart.device.output_line import GryfOutputLine

logging.basicConfig(
        level=logging.DEBUG
        )

_LOGGER = logging.getLogger(__name__)

async def main():
    """
    We can use to different approaches to control outputs:
        -   Using only GryfApi class,
        -   Creating devices (suggested),

    Create GryfApi is essential for 2 approaches.

    You can use serial connection(provide as an argument port) or using network (provide ip).
    """

    # network_api = GryfApi("192.168.40.95") 
    network_api = GryfApi("31.186.217.232")
    serial_api = GryfApi("/dev/ttyUSB0")

    await network_api.start_connection()

    output = GryfOutputLine("test" , network_api)
    output.subscribe(update)

    network_api.subscribe_output_message(update)

    """Using only GryfApi class."""

    id_out = 1
    pin_out = 1

    await network_api.set_out(id_out , pin_out , OutputActions.ON)

    await asyncio.sleep(1)

    await network_api.set_out(id_out , pin_out , OutputActions.OFF)

    await asyncio.sleep(1)

    await network_api.set_out(id_out , pin_out , OutputActions.TOGGLE)

    """Creating devices"""
    """
    If you using this metod you can get access to actual state with 
    the use of metod subscribe  which triggers the callback function,

    for example we use update function which logging actual state.
    """

    output_name = "output1"

    output_device = GryfOutput(output_name , id_out , pin_out , network_api)
    
    await output_device.turn_on()

    await asyncio.sleep(1)

    await output_device.turn_off()

    await asyncio.sleep(1)

    await output_device.toggle()

    """
    The next GryfApi module is "interval updates" which is recommended,
    because if the server loses connection for a momment, all data will
    be updated

    for argument you give time to update recommended is 5
    """

    network_api.start_update_interval(5)

    """
    GryfApi also supports GryfExpert system. this module allows to connect with 
    gryf expert program to program device.
    """

    await network_api.start_gryf_expert()
    await network_api.stop_gryf_expert()

async def update(state):
    _LOGGER.debug("Actual output state: %s" , state)

if __name__ == "__main__":
    asyncio.run(main())
