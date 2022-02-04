from dataclasses import dataclass
from typing import List, Optional, Union, Any
import discord
from .enums import *


@dataclass(frozen=True)
class InteractionData:
    id: Union[int, str]
    name: str
    type: int
    resolved: Optional[dict] = None
    options: Optional[dict] = None
    # below are only used for type != 2
    custom_id: Optional[str] = None
    component_type: Optional[int] = None
    values: Optional[list] = None
    # only used for User Command & Message Command
    target_id: Optional[str] = None


@dataclass(frozen=True)
class InteractionDataResolved:
    # only for extslash command
    users: Optional[dict] = None
    members: Optional[dict] = None
    roles: Optional[dict] = None
    channels: Optional[dict] = None
    messages: Optional[dict] = None


class InteractionDataOption:

    def __init__(
            self,
            data: dict,
            guild: discord.Guild,
            client: discord.Client,
            resolved: InteractionDataResolved,
    ):
        self._data = data
        self._guild = guild
        self._client = client
        self._resolved = resolved

    @property
    def name(self) -> str:
        return self._data.get('name')

    @property
    def type(self) -> int:
        return self._data.get('type')

    @property
    def value(
            self
    ) -> Union[
            str,
            int,
            float,
            bool,
            discord.User,
            discord.Role,
            discord.TextChannel,
            discord.VoiceChannel,
            discord.StageChannel,
            discord.CategoryChannel,
            discord.StoreChannel,
            discord.ChannelType,
    ]:

        if self.type == OptionType.SUBCOMMAND:
            return self._data.get('value')  # TODO: parse subcommand
        elif self.type == OptionType.SUBCOMMAND_GROUP:
            return self._data.get('value')  # TODO: parse subcommand group
        elif self.type == OptionType.STRING:
            return self._data.get('value')
        elif self.type == OptionType.INTEGER:
            return self._data.get('value')
        elif self.type == OptionType.BOOLEAN:
            return self._data.get('value')
        elif self.type == OptionType.USER:
            user_id = int(self._data.get('value'))
            return self._client.get_user(user_id)
        elif self.type == OptionType.CHANNEL:
            channel_id = int(self._data.get('value'))
            return self._guild.get_channel(channel_id)
        elif self.type == OptionType.ROLE:
            role_id = int(self._data.get('value'))
            return self._guild.get_role(role_id)
        elif self.type == OptionType.MENTIONABLE:
            some_id = self._data.get('value')
            user_data = self._resolved.users
            role_data = self._resolved.roles
            if user_data and user_data.get(some_id):
                return self._client.get_user(int(some_id))
            else:
                return self._guild.get_role(int(some_id))
        elif self.type == OptionType.NUMBER:
            return self._data.get('value')
        else:
            return self._data.get('value')

    @property
    def options(self) -> list:
        return self._data.get('options')

    @property
    def focused(self) -> bool:
        return self._data.get('focused')


@dataclass(frozen=True)
class BaseAppCommand:
    id: int
    name: str
    description: str
    type: int
    application_id: Optional[Union[int, str]]
    guild_id: Optional[Union[int, str]] = None
    options: Optional[list] = None
    default_permission: Optional[bool] = None
    version: Optional[Union[int, str]] = None
    default_member_permissions: Optional[list] = None
    dm_permission: Optional[bool] = None
    name_localizations: Optional = None
    description_localizations: Optional = None


@dataclass(frozen=True)
class BaseSlashPermission:
    id: Union[int, str]
    application_id: Union[int, str]
    guild_id: [Union[int, str]]
    permissions: list[dict]


@dataclass(frozen=True)
class SlashPermissionData:
    id: Union[int, str]
    type: int
    permission: bool


class SlashOverwrite:
    def __init__(self, data: dict):
        self._perms = BaseSlashPermission(**data)

    @property
    def command_id(self):
        return int(self._perms.id)

    @property
    def application_id(self):
        return int(self._perms.application_id)

    @property
    def guild_id(self):
        return int(self._perms.guild_id)

    @property
    def permissions(self):
        return [SlashPermissionData(**perm) for perm in self._perms.permissions]
