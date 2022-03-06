from .enums import ApplicationCommandType, PermissionType
from typing import List, Optional, Union, Dict
import discord


class BaseApplicationCommand:
    def __init__(self, name: str, type: ApplicationCommandType):
        self.name = name
        self.type = type
        if self.type is ApplicationCommandType.MESSAGE:
            self._qual = '__MESSAGE__' + name  # name for mapping
        elif self.type is ApplicationCommandType.USER:
            self._qual = '__USER__' + name  # name for mapping
        elif self.type is ApplicationCommandType.CHAT_INPUT:
            self._qual = '__CHAT__' + name


class Overwrite:
    def __init__(self, entity: Union[discord.Role, discord.User], *, allow: bool = True):
        if isinstance(entity, discord.Role):
            type_value = PermissionType.ROLE.value
        elif isinstance(entity, discord.User):
            type_value = PermissionType.USER.value
        else:
            raise TypeError('entity must be a discord.Role or discord.User')
        self._payload = {'id': str(entity.id), 'type': type_value, 'permission': allow}

    def to_dict(self):
        return self._payload
