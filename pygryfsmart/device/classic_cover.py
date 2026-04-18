import asyncio

from pygryfsmart import GryfApi
from pygryfsmart.const import ShutterStates, DriverFunctions

from .base import _GryfDevice

import logging

_LOGGER = logging.getLogger(__name__)

class Timer:
    _api: GryfApi
    _direction: int=0
    _time: int=0
    _defined: bool=False
    _shutter_position: float=0.0
    _percent_per_10_milisecounds: float
    _timer_on: bool=False
    _timer_callback_ptr = None
    _secound_timer_callback_ptr = None

    def __init__(self, api: GryfApi, time: int):
        self._api = api
        self._task = None

        self._percent_per_10_milisecounds = 100.0 / time

    def setup_timer(self, direction, time):
        self._direction = direction
        self._time = time

    def set_timer_callback(self, callback_ptr):
        self._timer_callback_ptr = callback_ptr

    def set_secound_timer_callback(self, callback_ptr):
        self._secound_timer_callback_ptr = callback_ptr

    async def __timer_task(self):
        time = self._time
        self._time = 0
        self._timer_on = True

        for i in range(time):
            if self._direction:
                self._shutter_position += self._percent_per_10_milisecounds
            else:
                self._shutter_position -= self._percent_per_10_milisecounds

            if self._timer_callback_ptr is not None:
                await self._timer_callback_ptr(self._shutter_position)

            if self._secound_timer_callback_ptr is not None:

                if self._shutter_position >= 0 and self._shutter_position <= 100:
                    await self._secound_timer_callback_ptr(self._shutter_position)
                elif self._shutter_position >= 0: 
                    await self._secound_timer_callback_ptr(0)
                else:
                    await self._secound_timer_callback_ptr(100)

            await asyncio.sleep(0.1)

        self._timer_on = False

    def start_timer(self):
        if self._time != 0:
            if self._task and not self._task.done():
                self._task.cancel()
            else:
                self._defined = True

            if self._direction:
                self._shutter_position += 7
            else:
                self._shutter_position -= 7

            self._task = asyncio.create_task(self.__timer_task())

    def stop_timer(self):
        if self._task and not self._task.done():
            self._task.cancel()

    @property
    def timer_enable(self):
        return self._timer_on

    @property
    def shutter_position(self):
        return self._shutter_position
    

class GryfCover(_GryfDevice):
    _is_opening: bool=False
    _is_closing: bool=False

    def __init__(
        self,
        name: str,
        id: int,
        pin: int,
        time: int,
        api: GryfApi,
        fun_ptr=None,
    ):
        super().__init__(name,
                         id,
                         pin,
                         api)

        self._time = time

        self._attributes = {
            "id": id,
            "pin": pin,
            "time": time
        }

        self._fun_ptr = fun_ptr
        self._api.subscribe(self._id , self._pin, DriverFunctions.COVER , self.__async_update)
        self._shutter_state = 0
        self._shutter_position = 0
        self._feedback_update = 0

        self._time_per_percent: float=time / 100.0
        self._timer = Timer(api, time)

    async def __async_update(self, state):
        self._feedback_update = 1
        self._timer.start_timer()

        if state == 0:
            self._timer.stop_timer()

        if state != 2 and state != 1:
            if self._shutter_state == 1:
                self._shutter_position = 1
            elif self._shutter_state == 2:
                self._shutter_position = 0

        self._shutter_state = state

        if self._fun_ptr:
            await self._fun_ptr(state)

    async def open_button_call(self):
        pass

    async def close_button_call(self):
        pass

    async def turn_on(self, time=None):
        if time is None:
            time = self._time

        self._timer.setup_timer(1, time)
        self._feedback_update = 0

        for k in range(5):
            await self._api.set_cover(self._id , self._pin , time , ShutterStates.OPEN)

            for i in range(10):
                if self._feedback_update:
                    return

                await asyncio.sleep((k + 1) * 0.03)

    async def turn_off(self, time=None):
        if time is None:
            time = self._time

        self._timer.setup_timer(0, time)
        self._feedback_update = 0

        for k in range(5):
            await self._api.set_cover(self._id , self._pin , time , ShutterStates.CLOSE)

            for i in range(10):
                if self._feedback_update:
                    return

                await asyncio.sleep((k + 1) * 0.03)

    async def toggle(self):
        if self._api._cover_toggle_metod:
            await self._api.set_cover(self._id , self._pin , self._time , ShutterStates.STEP_MODE)
        else:
            if self._shutter_position == 1:
                await self.turn_off()
            elif self._shutter_position == 0:
                await self.turn_on()

    async def stop(self, time: int | None=None):
        self._feedback_update = 0
        self._is_opening = False
        self._is_closing = False

        for k in range(5):
            if time is not None:
                await self._api.set_cover(self._id , self._pin , time , ShutterStates.STOP)
            else:
                await self._api.set_cover(self._id , self._pin , self._time , ShutterStates.STOP)

            for i in range(10):
                if self._feedback_update:
                    self._timer.stop_timer()
                    return

                await asyncio.sleep(k + 1 * 0.05)

    def subscribe(self , update_fun_ptr):
        self._fun_ptr = update_fun_ptr

    @property
    def name(self):
        return f"{self._name}"

class GryfPercentCover(GryfCover):
    _expected_position: int=0
    _current_position: float=0.0
    _tilt_opening_time: int=20
    _tilt_position_callback_ptr = None
    _tilt_position: float=0.0
    _tilt_waiting_to_set = False

    def __init__(
        self,
        name: str,
        id: int,
        pin: int,
        time: int,
        api: GryfApi,
        fun_ptr=None,
    ) -> None:
        super().__init__(
            name,
            id,
            pin,
            time,
            api,
            fun_ptr,
        )

        self._timer.set_timer_callback(self.callback_from_timer)

    def load_last_shutter_position(self, position):
        self._shutter_position = position

        self._timer._shutter_position = position
        self._current_position = position
        self._expected_position = position

        if position:
            self._current_cover_position = 100.0
        else:
            self._current_cover_position = 0.0


    def set_tilt_opening_time(self, time: int):
        self._tilt_opening_time = time

    def set_tilt_position_callback_ptr(self, ptr):
        self._tilt_position_callback_ptr = ptr

    async def set_cover_tilt_position(self, position: int):
        if not self._is_closing and not self._is_opening:
            if self._tilt_position > position:
                time = ((self._tilt_position - position) * (self._tilt_opening_time / 100.0)) + 7
                cover_potition = self._current_position - ((time / self._time) * 100.0)

                await self.set_cover_position(cover_potition)

            elif self._tilt_position < position:
                time = ((position - self._tilt_position) * (self._tilt_opening_time / 100.0)) - 7
                cover_potition = self._current_position + ((time / self._time) * 100.0)

                await self.set_cover_position(cover_potition)
        else:
            self._tilt_waiting_to_set = True

    async def set_cover_position(self, expected_position):

        if expected_position > self._current_position:
            if not self._is_opening:
                await self.turn_on()

            self._is_opening = True
            self._is_closing = False

        elif expected_position < self._current_position:
            if not self._is_closing:
                await self.turn_off()

            self._is_opening = False
            self._is_closing = True

        self._expected_position = expected_position

    async def callback_from_timer(self, position: float):

        self._current_position = position

        if (
            (self._is_opening and self._current_position >= self._expected_position)
            or
            (self._is_closing and self._current_position <= self._expected_position)
            or
            (self._current_position <= 0 or self._current_position > 99)
        ):

            if self._expected_position < 95 and self._expected_position > 5:
                await self.stop()

            self._is_opening = False
            self._is_closing = False

        if self._tilt_position < 100 and self._is_opening:
            self._tilt_position += (100.0 / self._tilt_opening_time)

            if self._tilt_position_callback_ptr is not None:
                await self._tilt_position_callback_ptr(self._tilt_position)
        elif self._tilt_position > 0 and self._is_closing:
            self._tilt_position -= (100.0 / self._tilt_opening_time)

            if self._tilt_position_callback_ptr is not None:
                await self._tilt_position_callback_ptr(self._tilt_position)

    @property
    def tilt_is_waiting_to_set(self):
        if self._tilt_waiting_to_set:
            self._tilt_waiting_to_set = False

            return True

        return False
