from pygryfsmart import GryfApi
from pygryfsmart.const import (
        CONF_OUT,
        CONF_TEMP,
        OUTPUT_STATES,
        )
from .base import _GryfDevice

from typing import Any

class GryfThermostat(_GryfDevice):

    _t_state: float
    _o_state = False

    def __init__(
        self,
        name: str,
        id: int,
        pin: int,
        temperature_id: int,
        temperature_pin: int,
        differential: int,
        api: GryfApi,
    ):
        super().__init__(name,
                         id,
                         pin,
                         api)
        self._t_id = temperature_id
        self._t_pin = temperature_pin
        self._update_fun_ptr = None | Any
        self._target_temperature = 0
        self._enable = False
        self._differential = differential

    def subscribe(self , update_fun_ptr):
        self._api.subscribe(self._id , self._pin, CONF_OUT , self.update_out)
        self._api.subscribe(self._t_id , self._t_pin, CONF_TEMP , self.update_temperature)
        self._update_fun_ptr = update_fun_ptr

    async def update_temperature(self , state):
        self._t_state = state

        data = {
            CONF_TEMP: self._t_state,
            CONF_OUT: self._o_state
        }

        if self._enable:
            if self._t_state > self._target_temperature + self._differential:
                await self._api.set_out(self._id , self._pin , OUTPUT_STATES.OFF)
            elif self._t_state < self._target_temperature - self._differential: 
                await self._api.set_out(self._id , self._pin , OUTPUT_STATES.ON)

        await self._update_fun_ptr(data)

    def enable(self , enable):
        self._enable = enable

    def set_target_temperature(self , temperature):
        self._target_temperature = temperature

    async def update_out(self , state):
        self._o_state = state

        data = {
            CONF_TEMP: self._t_state,
            CONF_OUT: self._o_state
        }

        await self._update_fun_ptr(data)

    @property
    def name(self):
        return f"{self._name}"

