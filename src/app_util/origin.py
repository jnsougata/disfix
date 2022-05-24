import discord
from .enums import ApplicationCommandType
from typing import Optional, Any, Union, List, Dict


class ApplicationCommandOrigin:

    def __init__(self, *, name: str, payload: Dict[str, Any], command_type: ApplicationCommandType):
        self.name = name
        self.type = command_type
        self._payload = payload
        if self.type is ApplicationCommandType.MESSAGE:
            self.uuid = '__MESSAGE__' + name
        elif self.type is ApplicationCommandType.USER:
            self.uuid = '__USER__' + name
        elif self.type is ApplicationCommandType.SLASH:
            self.uuid = '__CHAT__' + name

    def _inject_permission(self, permission: discord.Permissions):
        if permission:
            self._payload["default_member_permissions"] = str(permission.flag)
        else:
            self._payload["default_member_permissions"] = str(discord.Permissions.send_messages.flag)

    def _inject_subcommand(self, subcommand):
        self._payload['options'].append(subcommand.data)

    def to_dict(self):
        self._payload['type'] = self.type.value
        return self._payload
