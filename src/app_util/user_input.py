from .app import Overwrite, BaseApplicationCommand
from .enums import ApplicationCommandType


class UserCommand(BaseApplicationCommand):
    def __init__(
            self,
            *,
            name: str,
            default_access: bool = True,
            overwrites: [Overwrite] = None,
    ):
        self._map = 'USER_' + name.replace(" ", "_").upper()  # name for mapping
        self._payload = {
            'name': name,
            'type': ApplicationCommandType.USER.value,
            'default_permission': default_access,
        }
        self._overwrites = overwrites
        self.type = ApplicationCommandType.USER

    @property
    def overwrites(self):
        if self._overwrites:
            return {"permissions": [ow.to_dict() for ow in self._overwrites]}

    def to_dict(self) -> dict:
        return self._payload
