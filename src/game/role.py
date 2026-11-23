from enum import Enum

class Role(str, Enum):
    TOP = "TOP"
    JUNGLE = "JUNGLE"
    MID = "MID"
    BOT = "BOT"
    SUPPORT = "SUPPORT"