from dataclasses import dataclass
from typing import List, Optional, Union, Any
import discord
from enum import Enum
from discord.http import Route
from .enums import OptionType, ResolvedAttachment


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
    attachments: Optional[dict] = None


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
            ResolvedAttachment
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
        elif self.type == OptionType.ATTACHMENT:
            attachment_id = self._data.get('value')
            payload = self._resolved.attachments.get(attachment_id)
            return ResolvedAttachment(**payload)
        else:
            return self._data.get('value')

    @property
    def options(self) -> list:
        return self._data.get('options')

    @property
    def focused(self) -> bool:
        return self._data.get('focused')


class ApplicationCommand:
    def __init__(self, data: dict, client: discord.Client):
        self._payload = data
        self._client = client

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f'<ApplicationCommand id = {self.id} name = {self.name}>'

    @property
    def id(self) -> int:
        return self._payload.get('id')

    @property
    def name(self) -> str:
        return self._payload.get('name')

    @property
    def description(self) -> str:
        return self._payload.get('description')

    @property
    def type(self) -> int:
        return self._payload.get('type')

    @property
    def application_id(self) -> int:
        return int(self._payload.get('application_id'))

    @property
    def guild(self):
        guild_id = self._payload.get('guild_id')
        if guild_id:
            return self._client.get_guild(int(guild_id))
        else:
            return None

    @property
    def options(self) -> list:
        return self._payload.get('options')

    @property
    def default_permission(self) -> bool:
        return self._payload.get('default_permission')

    @property
    def version(self) -> int:
        return int(self._payload.get('version'))

    @property
    def default_member_permissions(self) -> list:
        return self._payload.get('default_member_permissions')

    @property
    def dm_permission(self) -> bool:
        return self._payload.get('dm_permission')

    @property
    def name_localizations(self):
        return self._payload.get('name_localizations')

    @property
    def description_localizations(self):
        return self._payload.get('description_localizations')

    @property
    def permissions(self):  # TODO: implement
        return self._payload.get('permissions')

    async def delete(self):
        if self.guild:
            route = Route('DELETE', f'/applications/{self.application_id}/guilds/{self.guild}/commands/{self.id}')
        else:
            route = Route('DELETE', f'/applications/{self.application_id}/commands/{self.id}')
        await self._client.http.request(route)



@dataclass(frozen=True)
class BasePermission:
    id: Union[int, str]
    application_id: Union[int, str]
    guild_id: [Union[int, str]]
    permissions: list[dict]


@dataclass(frozen=True)
class PermissionData:
    id: Union[int, str]
    type: int
    permission: bool


class Overwrite:
    def __init__(self, data: dict):
        self._perms = BasePermission(**data)

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
        return [PermissionData(**perm) for perm in self._perms.permissions]


class ApplicationCommandType(Enum):
    USER = 2
    MESSAGE = 3
    CHAT_INPUT = 1
