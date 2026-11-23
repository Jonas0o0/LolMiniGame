from enum import Enum


class GameStatus(str, Enum):
    EN_ATTENTE = "EN_ATTENTE"
    EN_COURS = "EN_COURS"
    TERMINEE = "TERMINEE"
    ANNULEE = "ANNULEE"


# Alias rétrocompatible
StatutPartie = GameStatus
