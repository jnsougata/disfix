from .app import Overwrite, ApplicationCommandOrigin
from .enums import ApplicationCommandType
import discord
from typing import Union, List, Optional


class UserCommand(ApplicationCommandOrigin):
    """
    Represents a user command. Pops up in the user context menu.
    """
    def __init__(
            self,
            name: str,
            *,
            dm_access: bool = True,
            permission: Optional[discord.Permissions] = None
    ):
        super().__init__(name, ApplicationCommandType.USER)
        self._payload = {
            'name': name,
            'type': ApplicationCommandType.USER.value,
            "dm_permission": dm_access,
            "default_member_permissions": str(permission.flag) if permission is not None else '0',
        }

    def to_dict(self) -> dict:
        return self._payload
