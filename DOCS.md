![GryfSmart logo](docs/logo.png)

# PYGRYFSMART LIB DATASHEET

pygryfsmart lib is lib who allows to control [GryfSmart](https://gryfsmart.pl) system using python. the base element of this lib is GryfApi object. All functions working using reference to this.

## GryfApi object

### Communication

pygryfsmart allows you to connect using serial or ethernet communication how to do this you can show in example.py 

#### Functions:

|function|working|
|--------|-------|
|start_connection() |Starting GryfApi Connection|
|stop_connection() |Stoping GryfApi Connection|
|start_gryf_expert() |Starting gryf expert server|
|stop_gryf_expert() |Stoping gryf expert server|
|subscribe(id: int, pin: int, func: str or DriverFunction, func_ptr) |Subscribe callback function|
|send_data() |Sending data to drivers|
|set_module_count(count: int) |Setting module count in network|
|subscribe_input_message(func_ptr) |Subscribe input messages from drivers|
|subscribe_output_message(func_ptr) |Subscribe output messages from drivers|
|start_update_interval(time: int) |Starting update interval|
|bool available_driver(id: int) |Returning available driver|
|bool available_driver(id: int) |Returning available driver|
|set_out(id: int, pin: int, state: int or OUTPUT_STATES)|setting output state|
|set_key_time(ps_time: int, pl_time: int, id: int, pin: int, type: KEY_MODE or int)|setting press short and long times|
|bool ping_connection()|Returning connection awailable|
|search_module(id: int)|Search module|
|search_moduls(last_id: int)|Search modules|
|ping(id: int)|Returning module available|
|set_pwm(id: int, pin: int, level: int)|Setting pwm state|
|set_cover(id: int, pin: int, time: int, operation: SHUTTER_STATES or int)|Setting cover state|
|reset(module_id: int , update_states_after: bool)|Reset all modules(id==0) or single|


