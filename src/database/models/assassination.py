from src.database.models.mini_game import MiniGame


class Assassination(MiniGame):
    __mapper_args__ = {
        "polymorphic_identity": "ASSASSINATION",
    }
