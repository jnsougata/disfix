import discord
from .origin import ApplicationCommandOrigin
from .enums import CommandType
from typing import Union, List, Optional


class UserCommand(ApplicationCommandOrigin):
    """
    Represents a user command. Pops up in the user context menu.
    """
    def __init__(self, name: str, *, dm_access: bool = True):
        self._payload = {
            'name': name,
            'type': None,
            "dm_permission": dm_access,
            "default_member_permissions": None,
        }
        super().__init__(name=name, payload=self._payload, command_type=CommandType.USER)
