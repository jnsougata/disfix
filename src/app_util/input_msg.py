from .app import Overwrite, ApplicationCommandOrigin
from .enums import ApplicationCommandType
import discord
from typing import Union, List, Optional


class MessageCommand(ApplicationCommandOrigin):
    """
    Represents a message command. Pops up in the message context menu.
    """
    def __init__(
            self,
            name: str,
            *,
            dm_access: bool = True,
            permissions: Optional[discord.Permissions] = None
    ):
        super().__init__(name, ApplicationCommandType.MESSAGE)
        self._payload = {
            'name': name,
            'type': self.type.value,
            "dm_permission": dm_access,
            "default_member_permissions": str(permissions.flag) if permissions is not None else '0',
        }

    def to_dict(self) -> dict:
        return self._payload
