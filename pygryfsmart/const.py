from enum import IntEnum , Enum

BAUDRATE = 115200

class OUTPUT_STATES(IntEnum):
    """Enum with Output states."""

    ON = 1
    OFF = 2
    TOGGLE = 3

class SCHUTTER_STATES(IntEnum):
    """Enum with Shutter states."""

    CLOSE = 1
    OPEN = 2
    STOP = 3
    STEP_MODE = 4

class KEY_MODE(IntEnum):
    "Enum with key modes."

    NO = 0
    NC = 1

class DriverFunctions(Enum):
    """Enum with driver functions."""

    INPUTS = "I"
    OUTPUTS = "O"
    PWM = "LED"
    COVER = "R"
    TEMP = "T"
    PONG = "PONG"

CONF_IN = "I"
CONF_OUT = "O"
CONF_PWM = "LED"
CONF_COVER = "R"
CONF_PRESS_SHORT = "PS"
CONF_PRESS_LONG = "PL"
CONF_TEMP = "T"
CONF_PONG = "PONG"

