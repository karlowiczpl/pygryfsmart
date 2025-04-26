"""File with GryfApi driver functions."""

from .const import (
    KEY_MODE,
    OUTPUT_STATES,
    SCHUTTER_STATES,

    COMMAND_FUNCTION_IN,
    COMMAND_FUNCTION_OUT,

    COMMAND_FUNCTION_SET_OUT,
    COMMAND_FUNCTION_SET_COVER,
    COMMAND_FUNCTION_SET_PWM,
    COMMAND_FUNCTION_PING,
    COMMAND_FUNCTION_SET_PRESS_TIME,
    COMMADN_FUNCTION_SEARCH_MODULE,
    COMMAND_FUNCTION_GET_OUT_STATE,
)
from .communications import _GryfCommunicationApiBase

import asyncio

class _GryfFunctionsApiBase(_GryfCommunicationApiBase):
    """GryfFunctionsApiBase."""
    
    def __init__(
            self,
            port: str,
            callback=None
        ) -> None:
        """Initialise GryfFunctionsApiBase."""

        super().__init__(port , callback=callback)

    async def set_out(
            self,
            id: int,
            pin: int,
            state: OUTPUT_STATES | int
        ) -> None:
        """Set driver output state."""

        states = ["0"] * 8 if pin > 6 else ["0"] * 6
        states[pin - 1] = str(state)

        command = f"{COMMAND_FUNCTION_SET_OUT}={id}," + ",".join(states) + "\n\r"
        await self.send_data(command)

        command = f"{COMMAND_FUNCTION_GET_OUT_STATE}={id}\n\r"
        await self.send_data(command)

    async def set_key_time(
            self,
            ps_time: int,
            pl_time: int,
            id: int,
            pin: int,
            type: KEY_MODE | int
        ) -> None:
        """Set target short and long press time for driver input."""

        command = f"{COMMAND_FUNCTION_SET_PRESS_TIME}={id},{pin},{ps_time},{pl_time},{type}\n\r"
        await self.send_data(command)

    async def ping_connection(self) -> bool:
        """Ping connection with drivers."""

        return await self.ping(1)

    async def search_module(
            self,
            id: int
        ) -> None:
        """Get model off current driver."""

        if id != 0:
            command = f"{COMMADN_FUNCTION_SEARCH_MODULE}=0,{id}\n\r"
            await self.send_data(command)
        else:
            await self.search_modules()

    async def search_modules(
            self,
            last_module: int | None=None
        ) -> None:
        """Get model off current drivers."""

        if last_module == None:
            module_count = max(len(self.feedback.data[COMMAND_FUNCTION_IN]), len(self.feedback.data[COMMAND_FUNCTION_OUT]))
        else:
            module_count = last_module

        for i in range(module_count):
            command = f"{COMMADN_FUNCTION_SEARCH_MODULE}=0,{i + 1}\n\r"
            await self.send_data(command)

    async def ping(
            self,
            module_id: int
        ) -> bool:
        """Ping single driver."""
        
        command = f"{COMMAND_FUNCTION_PING}={module_id}\n\r"
        await self.send_data(command)
        await asyncio.sleep(0.05)
        if self._last_ping == module_id:
            self._last_ping = 0
            return True
        self._last_ping = 0
        return False
    
    async def set_pwm(
            self,
            id: int,
            pin: int,
            level: int
        ) -> None:
        """Set current driver pwm output level."""

        command = f"{COMMAND_FUNCTION_SET_PWM}={id},{pin},{level}\n\r"
        await self.send_data(command)

    async def set_cover(
            self,
            id: int,
            pin: int,
            time: int,
            operation: SCHUTTER_STATES | int
        ) -> None:
        """Set current driver cover output state."""

        if operation in {SCHUTTER_STATES.CLOSE , SCHUTTER_STATES.OPEN , SCHUTTER_STATES.STOP , SCHUTTER_STATES.STEP_MODE} and pin in {1 , 2 , 3 , 4}:
            states = ["0"] * 4
            states[pin - 1] = str(operation)
            control_sum = id + time + int(states[0]) + int(states[1]) + int(states[2]) + int(states[3])

            command = f"{COMMAND_FUNCTION_SET_COVER}={id},{time},{states[0]},{states[1]},{states[2]},{states[3]},{control_sum}\n\r"
            await self.send_data(command)
        else:
            raise ValueError(f"Argument out of scope: id: {id} , pin: {pin} , time: {time}, operation: {operation}")

    async def reset(
            self,
            module_id: int,
            update_states: bool
        ) -> None:
        """Reset all drivers (module_id == 0) or single."""
        
        if module_id == 0:
            command = "AT+RST=0\n\r"
            await self.send_data(command)
            if update_states == True:
                module_count = len(self.feedback.data[COMMAND_FUNCTION_OUT])
                await asyncio.sleep(2)
                states = self.feedback.data[COMMAND_FUNCTION_OUT]
                for i in range(module_count):
                    tabble = list(self.feedback.data[COMMAND_FUNCTION_OUT][i+1].values())
                    states = ",".join(map(str, tabble))
                    command = f"AT+SetOut={i+1},{states}\n\r"
                    await self.send_data(command)
