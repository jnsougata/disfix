import discord
from dataclasses import dataclass
from typing import List, Optional, Union, Any
from enum import Enum
from discord.http import Route
from .enums import OptionType, ApplicationCommandType


def try_enum(enum_class, value):
    try:
        return enum_class(value)
    except ValueError:
        return None


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


class Resolved:
    def __init__(self, payload: dict, ctx):
        self._ctx = ctx
        self._payload = payload
        self._client = ctx._client

    @property
    def users(self) -> List[discord.User]:
        if self._payload.get('users'):
            return [
                discord.User(data=payload, state=self._client._connection)
                for payload in self._payload['users'].values()]

    @property
    def members(self) -> List[discord.Member]:
        if self._payload.get('members'):
            return [
                discord.Member(data=payload, state=self._client._connection)
                for payload in self._payload['members'].values()]

    @property
    def roles(self) -> List[discord.Role]:
        if self._payload.get('roles'):
            return [
                discord.Role(guild=self._ctx.guild, data=payload, state=self._client._connection)
                for payload in self._payload['roles'].values()]

    @property
    def channels(self):
        if self._payload.get('channels'):
            return [
                discord.abc.GuildChannel(data=payload, state=self._client._connection, guild=self._ctx.guild)
                for payload in self._payload['channels'].values()]

    @property
    def messages(self):
        if self._payload.get('messages'):
            return [
                discord.Message(data=payload, state=self._client._connection, channel=self._ctx.channel)
                for payload in self._payload['guilds'].values()]

    @property
    def attachments(self):
        if self._payload.get('attachments'):
            return [
                discord.Attachment(data=payload, state=self._client._connection)
                for payload in self._payload['attachments'].values()]


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


class InteractionDataOption:

    def __init__(
            self,
            data: dict,
            guild: discord.Guild,
            client: discord.Client,
            resolved: Resolved,
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
        str, int, float, bool,
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
        self.__payload = data
        self.__client = client
        self.id = int(data['id'])
        self.name = data['name']
        self.description = data['description']
        self.type = try_enum(ApplicationCommandType, data['type'])
        self.application_id = int(data['application_id'])
        self.options = data.get('options')
        self.version = int(data['version'])
        self.default_access = data['default_permission']
        self.dm_access = self.default_access or False
        self.permissions = data.get('permissions')
        self.name_locale = data['name_localizations']
        self.description_locale = data['description_localizations']

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f'<ApplicationCommand id = {self.id} name = {self.name}>'

    @property
    def guild(self):
        guild_id = self.__payload.get('guild_id')
        if guild_id:
            return self.__client.get_guild(int(guild_id))
        return None

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