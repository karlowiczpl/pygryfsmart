from enum import Enum

BAUDRATE = 115200

class OUTPUT_STATES(Enum):
    ON = 1,
    OFF = 2,
    TOGGLE = 3,

class SCHUTTER_STATES(Enum):
    CLOSE = 1,
    OPEN = 2,
    STOP = 3,
    STEP_MODE = 4

class KEY_MODE:
    NO = 0,
    NC = 1,
