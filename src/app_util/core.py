from __future__ import annotations
import sys
import discord
from .errors import *
from discord.ext import commands
from discord.http import Route
from dataclasses import dataclass
from .app import Overwrite, BaseApplicationCommand
from typing import List, Optional, Union, Any, Dict
from .enums import OptionType, ApplicationCommandType, PermissionType


def try_enum(enum_class, value):
    try:
        return enum_class(value)
    except ValueError:
        return None


def intflake(snowflake: str) -> Union[int, None]:
    try:
        return int(snowflake)
    except TypeError:
        return None


@dataclass(frozen=True)
class InteractionData:
    id: Union[int, str]
    name: str
    type: int
    resolved: Optional[dict] = None
    options: Optional[List[dict]] = None
    # below are only used for type != 2
    custom_id: Optional[str] = None
    component_type: Optional[int] = None
    values: Optional[list] = None
    # only used for User Command & Message Command
    target_id: Optional[str] = None


class Resolved:
    def __init__(self, payload: dict, ctx):
        self._ctx = ctx
        self._payload = payload
        self._client = ctx._client

    @property
    def users(self) -> Dict[int, discord.User]:
        if self._payload.get('users'):
            return {
                int(key): discord.User(
                    data=payload,
                    state=self._client._connection)
                for key, payload in self._payload['users'].items()}

    @property
    def members(self) -> Dict[int, discord.Member]:
        if self._payload.get('members'):
            return {
                int(key): self._ctx.guild.get_member(int(key))
                for key, _ in self._payload['members'].items()}

    @property
    def roles(self) -> Dict[int, discord.Role]:
        if self._payload.get('roles'):
            return {
                int(key): discord.Role(
                    guild=self._ctx.guild,
                    data=payload,
                    state=self._client._connection)
                for key, payload in self._payload['roles'].items()}

    @property
    def channels(self) -> Dict[int, discord.abc.GuildChannel]:
        if self._payload.get('channels'):
            return {
                int(key): self._ctx.guild.get_channel(int(key))
                for key, _ in self._payload['channels'].items()
            }

    @property
    def messages(self) -> Dict[int, discord.Message]:
        if self._payload.get('messages'):
            return {
                int(key): discord.Message(
                    data=payload,
                    state=self._client._connection,
                    channel=self._ctx.channel)
                for key, payload in self._payload['messages'].items()}

    @property
    def attachments(self) -> Dict[int, discord.Attachment]:
        if self._payload.get('attachments'):
            return {
                int(key): discord.Attachment(
                    data=payload,
                    state=self._client._connection)
                for key, payload in self._payload['attachments'].items()}


@dataclass(frozen=True)
class ResolvedAttachment:
    id: str = None
    filename: str = None
    description: str = None
    content_type: str = None
    size: int = None
    url: str = None
    proxy_url: str = None
    height: int = None
    width: int = None
    ephemeral: bool = None


class ChatInputOption:

    def __init__(
            self,
            data: Dict[str, Any],
            guild: discord.Guild,
            client: discord.Client,
            resolved: Resolved,
    ):
        self._data = data
        self._guild = guild
        self._client = client
        self._resolved = resolved

    def __repr__(self):
        return f'<ChatInputOption name={self.name} type={self.type}>'

    @property
    def name(self) -> str:
        return self._data.get('name')

    @property
    def type(self):
        value = self._data.get('type')
        return try_enum(OptionType, value)

    @property
    def value(self) -> Any:

        if self.type is OptionType.SUBCOMMAND:
            # TODO: parse subcommand
            return self._data.get('value')

        elif self.type is OptionType.SUBCOMMAND_GROUP:
            # TODO: parse subcommand group
            return self._data.get('value')

        elif self.type is OptionType.STRING:
            return self._data.get('value')

        elif self.type is OptionType.INTEGER:
            return self._data.get('value')

        elif self.type is OptionType.BOOLEAN:
            return self._data.get('value')

        elif self.type is OptionType.USER:
            user_id = int(self._data.get('value'))
            return self._resolved.users[user_id]

        elif self.type is OptionType.CHANNEL:
            channel_id = int(self._data.get('value'))
            return self._resolved.channels[channel_id]

        elif self.type is OptionType.ROLE:
            role_id = int(self._data.get('value'))
            return self._resolved.roles[role_id]

        elif self.type is OptionType.MENTIONABLE:
            target_id = int(self._data.get('value'))
            map = {}
            if not self._guild:
                if self._resolved.users:
                    map.update(self._resolved.users)
                if self._resolved.roles:
                    map.update(self._resolved.roles)
            else:
                if self._resolved.users:
                    map.update(self._resolved.users)
                if self._resolved.roles:
                    map.update(self._resolved.roles)
                if self._resolved.members:
                    map.update(self._resolved.members)
            return map[target_id]

        elif self.type is OptionType.NUMBER:
            return self._data['value']

        elif self.type is OptionType.ATTACHMENT:
            attachment_id = int(self._data['value'])
            return self._resolved.attachments[attachment_id]
        else:
            return self._data.get('value')

    @property
    def sub_options(self) -> list:
        return self._data.get('options')

    @property
    def focused(self) -> bool:
        return self._data.get('focused')


class ApplicationCommand:

    def __init__(self, client: commands.Bot, data: dict):
        self.__payload = data
        self.__client = client
        self.id = int(data['id'])
        self.guild_id = intflake(data.get('guild_id'))
        self.name = data['name']
        self.description = data['description']
        self.type = try_enum(ApplicationCommandType, data['type'])
        self.application_id = int(data['application_id'])
        self.options = data.get('options')
        self.version = int(data['version'])
        self.default_access = data['default_permission']
        self.dm_access = self.default_access or False
        self.permissions = data.get('permissions') or {}
        self.name_locale = data.get('name_localizations')
        self.description_locale = data.get('description_localizations')

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f'<ApplicationCommand id = {self.id} name = {self.name}>'

    @classmethod
    def _from_data(cls, client: commands.Bot, data: dict):
        return cls(client, data)

    @property
    def guild_specific(self) -> bool:
        if self.guild_id:
            return True
        return False

    @property
    def guild(self):
        if self.guild_id:
            return self.__client.get_guild(self.guild_id)
        return None

    def has_permission(self, guild: discord.Guild, entity: Union[discord.Role, discord.User]):
        permission = self.permissions.get(guild.id)
        if permission is None:
            return self.default_access
        for_entity = permission.get(entity.id)
        if for_entity is None:
            return self.default_access
        return for_entity

    async def delete(self):
        if self.guild:
            route = Route(
                'DELETE',
                f'/applications/{self.application_id}/guilds/{self.guild.id}/commands/{self.id}')
        else:
            route = Route(
                'DELETE',
                f'/applications/{self.application_id}/commands/{self.id}')

        await self.__client.http.request(route)
        self.__client._application_commands.pop(self.id)

    def _cache_overwrite(self, ows: dict, guild_id: int):
        self.permissions[guild_id] = {int(p['id']): p['permission'] for p in ows['permissions']}

    async def add_overwrites(self, overwrites: List[Overwrite], guild: discord.Guild = None):
        ows = {'permissions': [ow.to_dict() for ow in overwrites]}
        if self.guild_specific:
            r = Route('PUT',
                      f'/applications/{self.application_id}/guilds/{self.guild_id}/commands/{self.id}/permissions')
        elif guild:
            r = Route('PUT',
                      f'/applications/{self.application_id}/guilds/{guild.id}/commands/{self.id}/permissions')
        else:
            raise NoGuildProvided(f'Guild not provided while editing global command ({self.name})')

        data = await self.__client.http.request(r, json=ows)
        p = {int(p['id']): p['permission'] for p in data['permissions']}
        self.permissions[guild.id] = p


    async def update(self, command: BaseApplicationCommand) -> ApplicationCommand:
        if command.type is self.type:
            if self.guild_specific:
                r = Route('PATCH', f'/applications/{self.application_id}/guilds/{self.guild_id}/commands/{self.id}')
            else:
                r = Route('PATCH', f'/applications/{self.application_id}/commands/{self.id}')
            try:
                resp = await self.__client.http.request(r, json=command.to_dict())
            except discord.errors.HTTPException as e:
                raise e
            else:
                updated = self._from_data(self.__client, resp)
                self.__client._application_commands.pop(self.id)
                self.__client._application_commands[updated.id] = updated
                return updated
        else:
            raise TypeMismatch(f'Type mismatched while editing command `{self.name}` '
                               f'\nexpected: {self.type} | got: {command.type}')





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


class BaseOverwrite:
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
