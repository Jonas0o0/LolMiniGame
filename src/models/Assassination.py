from src.models.MiniGame import MiniGame


class Assassination(MiniGame):
    __mapper_args__ = {
        "polymorphic_identity": "ASSASSINATION",
    }
