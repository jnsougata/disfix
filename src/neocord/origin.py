import discord
from .enums import CommandType
from typing import Optional, Any, Union, List, Dict
from secrets import token_hex


class ApplicationCommandOrigin:

    def __init__(self, *, name: str, payload: Dict[str, Any], command_type: CommandType):
        self.name = name
        self.type = command_type
        self._payload = payload
        self._custom_id = token_hex(8)

    def _inject_permission(self, permission: discord.Permissions):
        if permission:
            self._payload["default_member_permissions"] = str(permission.flag)
        else:
            self._payload["default_member_permissions"] = str(discord.Permissions.send_messages.flag)

    def _inject_subcommand(self, subcommand):
        self._payload['options'].append(subcommand.data)

    def _inject_option(self, option):
        if self.type != CommandType.SLASH:
            raise TypeError("options are not allowed in context menu commands")
        self._payload["options"].append(option.data)

    def _inject_group(self, group):
        if self.type != CommandType.SLASH:
            raise TypeError("options are not allowed in context menu commands")
        self._payload["options"].append(group.data)

    def to_dict(self):
        self._payload['type'] = self.type.value
        return self._payload
