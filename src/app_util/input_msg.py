from .app import Overwrite, BaseApplicationCommand
from .enums import ApplicationCommandType


class MessageCommand(BaseApplicationCommand):
    """
    Represents a message command. Pops up in the message context menu.
    """
    def __init__(
            self,
            name: str,
            *,
            default_access: bool = True,
            overwrites: [Overwrite] = None,
    ):
        super().__init__(name, ApplicationCommandType.MESSAGE)
        self._payload = {
            'name': name,
            'type': self.type.value,
            'default_permission': default_access,
        }
        self._overwrites = overwrites


    @property
    def overwrites(self):
        if self._overwrites:
            return {"permissions": [ow.to_dict() for ow in self._overwrites]}

    def to_dict(self) -> dict:
        return self._payload
