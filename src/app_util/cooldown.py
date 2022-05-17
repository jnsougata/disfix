import datetime
import disocrd
from enums import Enum
from typing import Any, Union



class BucketType(Enum):
    GUILD = 1
    MEMBER = 2
    CHANNEL = 3


class Cooldown:

    def __init__(self, *, per: float, max: int, type: BucketType):
        self.per = per
        self.max = max
        self.type = type
        self.retry_after = 0


class CooldownHandler:

    __mapped_cooldowns__ = {}

    def __init__(self, cooldown: Cooldown):
        self.cooldown = cooldown


    def _set_last_invoke(self, key: int, value: Any, time: datetime.datetime):
        pass

    def _get_last_invoke(self, key: int, value: Any):
        pass

    def _get_invoke_count(self, key: int, value: Any):
        pass
