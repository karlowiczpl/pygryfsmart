import logging 

_LOGGER = logging.getLogger(__name__)

class Feedback:
    def __init__(self , callback=None) -> None:
        self._callback = callback
        self._data = {
            "IN": {},
            "OUT": {},
            "TEMP": {},
            "ROL": {},
            "PWM": {},
        }
    
    @property
    def data(self):
        return self.data
    async def __parse_metod_1(self , parsed_states , line , function: str):
        if len(parsed_states) not in {7 , 9}:
            raise ValueError(f"Invalid number of arguments: {line}")

        for i in range(1, len(parsed_states)):
            if parsed_states[i] not in {"0" , "1"}:
                raise ValueError(f"Wrong parameter value: {line}")

            pin = int(parsed_states[0])
            if pin not in self._data[function]:
            if pin not in self._data[function]:
            self._data[function][pin][i] = int(parsed_states[i])                   

    async def input_data(self , line):
        if line == "??????????":
            return
        try:
            parts = line.split('=')
            parsed_states = parts[1].split(',')
            last_state = parsed_states[-1].split(';')
            parsed_states[-1] = last_state[0]

            if parts[0] == "I":
                await self.__parse_metod_1(parsed_states , line , F)

            if parts[0] == "O":
                if len(parsed_states) not in {7 , 9}:
                    raise ValueError(f"Invalid number of arguments: {line}")

                for i in range(1, len(parsed_states)):
                    if parsed_states[i] not in {"0" , "1"}: 
                        raise ValueError(f"Wrong parameter value: {line}")

                    pin = int(parsed_states[0])
                    if pin not in self._data["OUT"]:
                        self._data["OUT"][pin] = {}
                    self._data["OUT"][pin][i] = int(parsed_states[i])                   

            if parts[0] == "PS":
                if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
                    raise ValueError(f"Argument out of scope: {line}")

                pin = int(parsed_states[1])
                id = int(parsed_states[0])
                if id not in self._data["IN"]:
                    self._data["IN"][id] = {}
                self._data["IN"][id][pin] = 2

            if parts[0] == "PL":
                if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
                    raise ValueError(f"Argument out of scope: {line}")

                pin = int(parsed_states[1])
                id = int(parsed_states[0])
                if id not in self._data["IN"]:
                    self._data["IN"][id] = {}
                self._data["IN"][id][pin] = 3

            if parts[0] == "T":
                if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
                    raise ValueError(f"Argument out of scope: {line}")

                pin = int(parsed_states[1])
                id = int(parsed_states[0])
                if id not in self._data["TEMP"]:
                    self._data["TEMP"][id] = {}
                self._data["TEMP"][id][pin] = float(f"{parsed_states[2]}.{parsed_states[3]}")

            if parts[0] == "PONG":
                self._last_ping = int(parsed_states[0])

            _LOGGER.debug(f"Parsed data: {self._data}")

            if self._callback:
                await self._callback(line) 
        except Exception as e:
            _LOGGER.error(f"ERROR parsing data: {e}")
