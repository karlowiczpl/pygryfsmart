from datetime import datetime
import logging
from typing import Any

from pygryfsmart.api import GryfApi
from pygryfsmart.const import (
    COMMAND_FUNCTION_PONG,
    COMMAND_FUNCTION_PWM,
    COMMAND_FUNCTION_TEMP,
    CONF_OUT,
    CONF_TEMPERATURE,
    OUTPUT_STATES,
    COMMAND_FUNCTION_IN,
    COMMAND_FUNCTION_OUT,
)

_LOGGER = logging.getLogger(__name__)

class _GryfDevice:
    _name: str
    _id: int
    _pin: int
    _api: GryfApi

    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 api: GryfApi
                 ) -> None:
        self._name = name
        self._id = id
        self._pin = pin
        self._api = api

        now = datetime.now()
        self._api.feedback.data[COMMAND_FUNCTION_PONG][self._id] = now.strftime("%H:%M") 

    @property
    def available(self):
        return self._api.avaiable_module(self._id)

class _GryfOutput(_GryfDevice):
    def __init__(
        self,
        name: str,
        id: int,
        pin: int,
        api: GryfApi,
    ):
        super().__init__(name,
                         id,
                         pin,
                         api)

    def subscribe(self , update_fun_ptr):
        self._api.subscribe(self._id , self._pin, COMMAND_FUNCTION_OUT , update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}"

    async def turn_on(self):
        await self._api.set_out(self._id, self._pin, OUTPUT_STATES.ON)

    async def turn_off(self):
        await self._api.set_out(self._id, self._pin, OUTPUT_STATES.OFF)

    async def toggle(self):
        await self._api.set_out(self._id, self._pin, OUTPUT_STATES.TOGGLE)

class _GryfInput(_GryfDevice):

    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 api: GryfApi,
                 ) -> None:
        super().__init__(name,
                         id,
                         pin,
                         api)

    def subscribe(self , update_fun_ptr):
        self._api.subscribe(self._id , self._pin, COMMAND_FUNCTION_IN , update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}"

class _GryfTemperature(_GryfDevice):
    
    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 api: GryfApi,
                 ) -> None:
        super().__init__(name, 
                         id, 
                         pin, 
                         api)

    def subscribe(self , update_fun_ptr):
        self._api.subscribe(self._id , self._pin, COMMAND_FUNCTION_TEMP , update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}"

class _GryfPwm(_GryfDevice):
    
    _last_level: int
    _is_on: bool

    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 api: GryfApi,
                 ) -> None:
        super().__init__(name, 
                         id, 
                         pin, 
                         api)
        self._last_level = 0
        self._is_on = False

    def subscribe(self , update_fun_ptr):
        self._api.subscribe(self._id , self._pin, COMMAND_FUNCTION_PWM , update_fun_ptr)

    async def set_level(self , level: int):
        if level > 0:
            self._last_level = level
        await self._api.set_pwm(self._id , self._pin , level)

    async def turn_on(self):
        await self._api.set_pwm(self._id , self._pin , self._last_level)
        self._is_on = True

    async def turn_off(self):
        await self._api.set_pwm(self._id , self._pin , 0)
        self._is_on = False

    async def toggle(self):
        if self._is_on:
            await self.turn_off()
        else:
            await self.turn_on()

    @property
    def name(self):
        return f"{self._name}"

class _GryfInputLine(_GryfDevice):
    
    def __init__(self,
                 name: str,
                 api: GryfApi,
                 ) -> None:
        super().__init__(name, 
                         0, 
                         0, 
                         api)

    def subscribe(self , update_fun_ptr):
        self._api.subscribe_input_message(update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}"

class _GryfOutputLine(_GryfDevice):
    
    def __init__(self,
                 name: str,
                 api: GryfApi,
                 ) -> None:
        super().__init__(name, 
                         0, 
                         0, 
                         api)

    def subscribe(self , update_fun_ptr):
        self._api.subscribe_output_message(update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}"

class _GryfThermostat(_GryfDevice):

    _t_state: float
    _o_state: bool

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
        self._api.subscribe(self._id , self._pin, COMMAND_FUNCTION_OUT , update_fun_ptr)
        self._api.subscribe(self._t_id , self._t_pin, COMMAND_FUNCTION_TEMP , update_fun_ptr)
        self._update_fun_ptr = update_fun_ptr

    async def update_temperature(self , state):
        self._t_state = state

        data = {
            CONF_TEMPERATURE: self._t_state,
            CONF_OUT: self._o_state
        }
        
        if self._enable:
            if self._target_temperature + self._differential > self._t_state:
                await self._api.set_out(self._id , self._pin , OUTPUT_STATES.OFF)
            elif self._target_temperature - self._differential < self._t_state:
                await self._api.set_out(self._id , self._pin , OUTPUT_STATES.ON)

        await self._update_fun_ptr(data)

    def enable(self , enable):
        self._enable = enable
        
    def set_target_temperature(self , temperature):
        self._target_temperature = temperature

    async def update_out(self , state):
        self._o_state = state

        data = {
            CONF_TEMPERATURE: self._t_state,
            CONF_OUT: self._o_state
        }
        
        await self._update_fun_ptr(data)

    @property
    def name(self):
        return f"{self._name}"
