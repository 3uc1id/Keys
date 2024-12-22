from enum import IntEnum
from math import tau as TAU

F_SAMPLE = 44100
BUFFLEN = 256
BUFFLEN_T = BUFFLEN / F_SAMPLE  # length of the buffer in seconds



class SynthCommand(IntEnum):
    START_NOTE = 0
    STOP_NOTE = 1
    SET_BUFFER_SIZE = 2
    SET_SAMPLING_RATE = 3
    STOP_SYNTHESIZER = 4

NOTE_TABLE = {
    "C4": 261.6255653005986,
    "C4#": 277.1826309768721,
    "D4": 293.6647679174076,
    "D4#": 311.1269837220809,
    "E4": 329.6275569128699,
    "F4": 349.2282314330039,
    "F4#": 369.9944227116344,
    "G4": 391.99543598174927,
    "G4#": 415.3046975799451,
    "A4": 440.0,
    "A4#": 466.1637615180899,
    "B4": 493.8833012561241,
    "C5": 523.2511306011972,
    "C5#": 554.3652619537442,
    "D5": 587.3295358348151,
    "D5#": 622.2539674441618,
    "E5": 659.2551138257398,
    "F5": 698.4564628660078,
    "F5#": 739.9888454232688,
    "G5": 783.9908719634985,
    "G5#": 830.6093951598903,
    "A5": 880.0,
    "A5#": 932.3275230361799,
    "B5": 987.7666025122483,
}

