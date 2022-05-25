from .origin import ApplicationCommandOrigin
from .enums import CommandType
import discord
from typing import Union, List, Optional


class MessageCommand(ApplicationCommandOrigin):
    """
    Represents a message command. Pops up in the message context menu.
    """
    def __init__(self, name: str, *, dm_access: bool = True):
        self._payload = {
            'name': name,
            'type': None,
            "dm_permission": dm_access,
            "default_member_permissions": None,
        }
        super().__init__(name=name, payload=self._payload, command_type=CommandType.MESSAGE)
