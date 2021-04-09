mode_c_transmission_speeds: dict[str, int] = {
    "0": 300,
    "1": 600,
    "2": 1200,
    "3": 2400,
    "4": 4800,
    "5": 9600,
    "6": 19200,
}

mode_c_transmission_ids = {
    speed: identifier for identifier, speed in mode_c_transmission_speeds.items()
}
