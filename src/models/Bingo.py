from src.models.MiniGame import MiniGame


class Bingo(MiniGame):
    __mapper_args__ = {
        "polymorphic_identity": "BINGO",
    }
